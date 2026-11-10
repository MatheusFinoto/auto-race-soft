import io
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import call, patch

import numpy as np
from PIL import Image
import pyscreeze

from src import actions, utils
from src.auto_race import auto_race


class AutoRaceMathTest(unittest.TestCase):
    def setUp(self):
        self.box = SimpleNamespace(left=100, top=200, width=596, height=125)
        self.click = self.start_patch("src.utils.human_click")
        self.press = self.start_patch("src.utils.keyboard.press_and_release")
        self.screenshot = self.start_patch("src.utils.pyautogui.screenshot")
        self.screenshot.return_value = Image.new("RGB", (40, 40), "black")
        self.ocr = self.start_patch("src.utils.pytesseract.image_to_string")
        self.start_patch(
            "src.utils.pyautogui.position",
            side_effect=AssertionError("A soma deve usar a origem do diálogo"),
        )
        self.output = io.StringIO()
        self.start_context(redirect_stdout(self.output))

    def start_patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        result = patcher.start()
        self.addCleanup(patcher.stop)
        return result

    def start_context(self, context):
        context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)

    def test_dispatch_reads_templates_and_sends_sum(self):
        templates = Path(__file__).resolve().parents[1] / "images" / "awnsers"
        images = []
        for number in (59, 53):
            with Image.open(templates / f"{number}.png") as image:
                images.append(image.convert("RGB"))
        self.screenshot.side_effect = images

        result = actions.switch_field_action(
            {"field": "ar_field_step_3", "box": self.box}
        )

        self.assertTrue(result)
        self.assertEqual(
            self.screenshot.call_args_list,
            [call(region=(124, 334, 40, 40)), call(region=(174, 334, 40, 40))],
        )
        self.assertEqual(self.press.call_args_list, [call("1"), call("1"), call("2")])
        self.assertEqual(
            self.click.call_args_list,
            [call((298, 353), jitter=2), call(563, 463)],
        )
        self.ocr.assert_not_called()
        self.assertIn("SUCESSO STEP 3", self.output.getvalue())

    def test_numpy_box_coordinates_work_with_windows_screenshot(self):
        box = pyscreeze.Box(np.int64(100), np.int64(200), np.int64(596), np.int64(125))
        templates = Path(__file__).resolve().parents[1] / "images" / "awnsers"
        frame = Image.new("RGB", (640, 480), "black")
        for number, left in ((59, 124), (53, 174)):
            with Image.open(templates / f"{number}.png") as image:
                frame.paste(image, (left, 334))
        self.screenshot.side_effect = pyscreeze._screenshot_win32
        with patch("pyscreeze.ImageGrab.grab", return_value=frame):
            result = auto_race.do_ar_step_3(box)

        self.assertTrue(result)
        for captured in self.screenshot.call_args_list:
            self.assertTrue(all(type(value) is int for value in captured.kwargs["region"]))
        self.assertEqual(self.press.call_args_list, [call("1"), call("1"), call("2")])
        self.assertEqual(
            self.click.call_args_list,
            [call((298, 353), jitter=2), call(563, 463)],
        )
        self.ocr.assert_not_called()

    def test_numpy_region_is_normalized_before_windows_screenshot(self):
        templates = Path(__file__).resolve().parents[1] / "images" / "awnsers"
        frame = Image.new("RGB", (100, 100), "black")
        with Image.open(templates / "53.png") as image:
            frame.paste(image, (20, 30))
        self.screenshot.side_effect = pyscreeze._screenshot_win32
        region = tuple(np.int64(v) for v in (20, 30, 40, 40))
        with patch("pyscreeze.ImageGrab.grab", return_value=frame):
            with self.assertRaisesRegex(AssertionError, "region argument must be a tuple of four ints"):
                pyscreeze._screenshot_win32(region=region)
            number = utils.extract_number_from_region(region)

        self.assertEqual(number, 53)
        self.assertTrue(all(type(value) is int for value in self.screenshot.call_args.kwargs["region"]))
        self.press.assert_not_called()
        self.click.assert_not_called()
        self.ocr.assert_not_called()

    def test_ocr_fallback_prepares_small_number_image(self):
        self.ocr.return_value = " 59\n"
        with (
            patch.object(utils, "AWNSERS_CACHE", []),
            patch.object(utils.DIGIT_TEMPLATES, "read_number", return_value=None),
        ):
            number = utils.extract_number_from_region((124, 334, 40, 40))

        self.assertEqual(number, 59)
        self.ocr.assert_called_once()
        prepared = self.ocr.call_args.args[0]
        self.assertEqual(prepared.size, (380, 380))
        self.assertEqual(prepared.mode, "L")
        self.assertEqual(
            self.ocr.call_args.kwargs["config"],
            "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789",
        )

    def test_unreadable_second_operand_does_not_send_partial_answer(self):
        self.ocr.side_effect = ["59", ""]
        with (
            patch.object(utils, "AWNSERS_CACHE", []),
            patch.object(utils.DIGIT_TEMPLATES, "read_number", return_value=None),
        ):
            result = auto_race.do_ar_step_3(self.box)

        self.assertFalse(result)
        self.press.assert_not_called()
        self.click.assert_called_once_with((298, 353), jitter=2)
        self.assertNotIn("SUCESSO STEP 3", self.output.getvalue())

    def test_ocr_error_does_not_send_or_confirm_answer(self):
        self.ocr.side_effect = RuntimeError("OCR indisponível")
        with (
            patch.object(utils, "AWNSERS_CACHE", []),
            patch.object(utils.DIGIT_TEMPLATES, "read_number", return_value=None),
        ):
            result = auto_race.do_ar_step_3(self.box)

        self.assertFalse(result)
        self.press.assert_not_called()
        self.click.assert_called_once_with((298, 353), jitter=2)
        self.assertNotIn("SUCESSO STEP 3", self.output.getvalue())

    def test_fragmented_ocr_number_does_not_send_partial_answer(self):
        self.ocr.side_effect = ["5 9", "7"]
        with (
            patch.object(utils, "AWNSERS_CACHE", []),
            patch.object(utils.DIGIT_TEMPLATES, "read_number", return_value=None),
        ):
            result = auto_race.do_ar_step_3(self.box)

        self.assertFalse(result)
        self.press.assert_not_called()
        self.click.assert_called_once_with((298, 353), jitter=2)
        self.assertNotIn("SUCESSO STEP 3", self.output.getvalue())

    def test_unseen_number_is_summed_without_whole_number_templates_or_ocr(self):
        templates = Path(__file__).resolve().parents[1] / "images" / "awnsers"
        first = Image.new("RGB", (40, 40), (25, 55, 85))
        for digit, left in ((9, 13), (7, 20)):
            with Image.open(templates / f"{digit}.png") as image:
                first.paste(image.crop((13, 9, 19, 18)), (left, 9))
        with Image.open(templates / "7.png") as image:
            second = image.convert("RGB")
        self.screenshot.side_effect = [first, second]
        with patch.object(utils, "AWNSERS_CACHE", []):
            result = auto_race.do_ar_step_3(self.box)

        self.assertTrue(result)
        self.assertEqual(self.press.call_args_list, [call("1"), call("0"), call("4")])
        self.assertEqual(
            self.click.call_args_list,
            [call((298, 353), jitter=2), call(563, 463)],
        )
        self.ocr.assert_not_called()


if __name__ == "__main__":
    unittest.main()
