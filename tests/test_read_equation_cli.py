import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image

from src.auto_race.equation import Addition
from src.auto_race.local_reader import LocalReadError
from src.read_equation import main


class ReadEquationCliTest(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "soma.png"
        Image.new("RGB", (100, 40), "white").save(self.path)
        self.output = io.StringIO()
        self.errors = io.StringIO()
        self.enterContext(redirect_stdout(self.output))
        self.enterContext(redirect_stderr(self.errors))
        self.factory = self.enterContext(
            patch("src.read_equation.LocalEquationReader")
        )
        self.reader = self.factory.return_value

    def test_reads_files_and_computes_all_five_example_sums(self):
        self.reader.read_equation.side_effect = [
            Addition(26, 40), Addition(62, 2), Addition(23, 46),
            Addition(78, 43), Addition(29, 31),
        ]

        result = main([str(self.path)] * 5)

        self.assertEqual(result, 0)
        self.assertEqual(self.reader.read_equation.call_count, 5)
        for equation in ("26 + 40 = 66", "62 + 2 = 64", "23 + 46 = 69",
                         "78 + 43 = 121", "29 + 31 = 60"):
            self.assertIn(equation, self.output.getvalue())
        self.assertEqual(self.errors.getvalue(), "")

    def test_crop_reads_only_selected_pixels(self):
        image = Image.new("RGB", (100, 40), "black")
        image.paste("white", (20, 5, 70, 30))
        image.save(self.path)
        self.reader.read_equation.return_value = Addition(26, 40)

        result = main([
            str(self.path), "--crop", "20", "5", "50", "25",
        ])

        self.assertEqual(result, 0)
        self.factory.assert_called_once_with()
        sent = self.reader.read_equation.call_args.args[0]
        self.assertEqual(sent.size, (50, 25))
        self.assertEqual(sent.getextrema(), ((255, 255), (255, 255), (255, 255)))

    def test_missing_dependency_reports_configuration_failure(self):
        self.factory.side_effect = LocalReadError("Instale ddddocr para usar o OCR local.")

        self.assertEqual(main([str(self.path)]), 1)

        self.assertIn("ddddocr", self.errors.getvalue())
        self.reader.read_equation.assert_not_called()

    def test_invalid_crop_is_rejected_before_reader_initialization(self):
        for crop in ((-1, 0, 10, 10), (0, -1, 10, 10), (0, 0, 0, 10), (0, 0, 10, -1)):
            with self.subTest(crop=crop), self.assertRaises(SystemExit) as raised:
                main([str(self.path), "--crop", *map(str, crop)])
            self.assertEqual(raised.exception.code, 2)
        self.factory.assert_not_called()

    def test_crop_outside_image_does_not_make_a_request(self):
        self.assertEqual(main([str(self.path), "--crop", "90", "0", "20", "10"]), 1)

        self.reader.read_equation.assert_not_called()
        self.assertIn("limites", self.errors.getvalue())

    def test_missing_or_invalid_image_does_not_make_a_request(self):
        invalid = Path(self.directory.name) / "invalida.png"
        invalid.write_text("arquivo sem imagem", encoding="utf-8")

        self.assertEqual(main([str(invalid), str(invalid.with_name("ausente.png"))]), 1)

        self.reader.read_equation.assert_not_called()
        self.assertEqual(self.errors.getvalue().count("não foi possível abrir"), 2)

    def test_unreadable_image_is_not_reported_as_a_result(self):
        self.reader.read_equation.return_value = None

        self.assertEqual(main([str(self.path)]), 1)

        self.assertEqual(self.output.getvalue(), "")
        self.assertIn("não foi possível ler", self.errors.getvalue())

    def test_model_failure_preserves_nonzero_exit_for_batch(self):
        self.reader.read_equation.side_effect = [
            LocalReadError("Falha no reconhecimento local."), Addition(62, 2),
        ]

        self.assertEqual(main([str(self.path), str(self.path)]), 1)

        self.assertIn("Falha no reconhecimento local", self.errors.getvalue())
        self.assertIn("62 + 2 = 64", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
