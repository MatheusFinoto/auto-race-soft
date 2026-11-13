from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from PIL import Image, ImageDraw, ImageOps

from src.auto_race.equation import Addition
from src.auto_race.local_reader import LocalEquationReader, LocalReadError, _decode_prediction


FIXTURES = Path(__file__).parent / "fixtures" / "equations"


def prediction(text, confidence=0.99):
    charset = ["", *dict.fromkeys("0123456789+=xot")]
    probabilities = []
    for character in text:
        row = [0.0] * len(charset)
        row[charset.index(character)] = confidence
        row[0] = 1.0 - confidence
        probabilities.extend([row, row])
        blank = [0.0] * len(charset)
        blank[0] = 1.0
        probabilities.append(blank)
    return {"charset": charset, "probabilities": [[row] for row in probabilities]}


class LocalEquationReaderTest(unittest.TestCase):
    def setUp(self):
        self.engine = Mock()
        self.reader = LocalEquationReader(engine=self.engine)
        self.image = Image.new("L", (90, 36), 238)
        ImageDraw.Draw(self.image).rectangle((5, 5, 70, 29), fill=22)

    def test_ctc_collapses_repeats_but_preserves_digits_separated_by_blank(self):
        self.assertEqual(_decode_prediction(prediction("11+22")).addition, Addition(11, 22))

    def test_complete_consistent_expression_computes_sum(self):
        self.engine.classification.return_value = prediction("26+40")
        self.assertEqual(self.reader.read_equation(self.image), Addition(26, 40))
        self.assertEqual(self.engine.classification.call_count, 3)
        self.assertTrue(self.engine.classification.call_args.kwargs["probability"])

    def test_unknown_characters_are_rejected_instead_of_removed_or_replaced(self):
        for text in ("26x40", "26t40", "26+4o", "2o6+40", "2640", "26+40=66"):
            with self.subTest(text=text):
                self.engine.classification.return_value = prediction(text)
                self.assertIsNone(self.reader.read_equation(self.image))

    def test_each_character_must_meet_confidence_and_margin(self):
        self.assertIsNone(_decode_prediction(prediction("26+40", confidence=0.60)))
        uncertain = prediction("26+40", confidence=0.68)
        for step in uncertain["probabilities"]:
            row = step[0]
            if row[uncertain["charset"].index("+")] > 0:
                row[0] = 0
                row[uncertain["charset"].index("x")] = 0.60
        self.assertIsNone(_decode_prediction(uncertain))

    def test_disagreeing_valid_readings_never_produce_an_answer(self):
        self.engine.classification.side_effect = [
            prediction("26+40"), prediction("28+40"), prediction("26+40"),
        ]
        self.assertIsNone(self.reader.read_equation(self.image))

    def test_one_candidate_needs_higher_confidence_when_others_are_unreadable(self):
        for confidence, expected in ((0.80, None), (0.95, Addition(26, 40))):
            with self.subTest(confidence=confidence):
                self.engine.classification.side_effect = [
                    prediction("26+40", confidence), prediction("2640"), prediction("2640"),
                ]
                self.assertEqual(self.reader.read_equation(self.image), expected)

    def test_identical_images_are_not_counted_as_extra_votes(self):
        image = Image.new("L", (90, 36), 255)
        ImageDraw.Draw(image).rectangle((5, 5, 70, 29), fill=0)
        self.engine.classification.side_effect = [
            prediction("2640"), prediction("26+40", 0.80), prediction("26+40", 0.80),
        ]
        self.assertIsNone(self.reader.read_equation(image))
        self.assertEqual(self.engine.classification.call_count, 2)

    def test_blank_tiny_or_transparent_empty_images_do_not_run_the_model(self):
        for image in (
            Image.new("L", (90, 36), 255), Image.new("L", (4, 4), 0),
            Image.new("RGBA", (90, 36), (0, 0, 0, 0)),
        ):
            self.assertIsNone(self.reader.read_equation(image))
        self.engine.classification.assert_not_called()

    def test_model_failure_or_invalid_output_is_reported(self):
        self.engine.classification.side_effect = RuntimeError("internal-details")
        with self.assertRaisesRegex(LocalReadError, "executar") as caught:
            self.reader.read_equation(self.image)
        self.assertNotIn("internal-details", str(caught.exception))
        self.engine.classification.side_effect = None
        for value in ("26+40", {}, {"charset": [""], "probabilities": []}):
            with self.subTest(value=value):
                self.engine.classification.return_value = value
                with self.assertRaises(LocalReadError):
                    self.reader.read_equation(self.image)

    def test_invalid_probabilities_are_rejected(self):
        for value in (float("nan"), float("inf"), -0.1, 1.1):
            payload = prediction("26+40")
            payload["probabilities"][0][0][1] = value
            with self.subTest(value=value), self.assertRaises(LocalReadError):
                _decode_prediction(payload)


class LocalModelRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader = LocalEquationReader()

    def test_real_cpu_model_on_synthetic_images_without_network(self):
        paths = sorted(FIXTURES.glob("*.png"))
        self.assertEqual(len(paths), 40)
        recognized = 0
        with patch("socket.socket.connect", side_effect=AssertionError("A leitura deve ser local")):
            for path in paths:
                left, right = (int(value) for value in path.stem.split("_")[-2:])
                with self.subTest(image=path.name), Image.open(path) as image:
                    result = self.reader.read_equation(image)
                    if result is not None:
                        self.assertEqual(result, Addition(left, right))
                        recognized += 1
        self.assertGreaterEqual(recognized, 29)

    def test_five_noisy_bold_examples_are_read_by_real_model(self):
        for left, right in ((26, 40), (62, 2), (23, 46), (78, 43), (29, 31)):
            path = FIXTURES / f"timesbd_noise_{left}_{right}.png"
            with self.subTest(image=path.name), Image.open(path) as image:
                self.assertEqual(self.reader.read_equation(image), Addition(left, right))

    def test_light_text_on_dark_background_preserves_result(self):
        with Image.open(FIXTURES / "timesbd_clean_26_40.png") as image:
            self.assertEqual(self.reader.read_equation(ImageOps.invert(image)), Addition(26, 40))


if __name__ == "__main__":
    unittest.main()
