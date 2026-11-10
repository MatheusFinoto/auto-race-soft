from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import pyautogui
import pyscreeze

from src import actions, utils


class FieldDetectionTest(unittest.TestCase):
    def setUp(self):
        pixels = np.random.default_rng(7).integers(0, 256, (60, 80, 3), dtype=np.uint8)
        self.screen = Image.fromarray(pixels)
        self.needle = self.screen.crop((20, 15, 50, 35))
        self.region = (10, 10, 50, 40)

    def test_oversized_template_is_skipped_after_real_matcher_error(self):
        oversized = Image.new("RGB", (60, 20), "black")
        with patch("pyscreeze.screenshot", return_value=self.screen):
            with self.assertRaisesRegex(ValueError, "needle dimension"):
                pyautogui.locateOnScreen(oversized, confidence=0.9, region=self.region)

            self.assertIsNone(actions.safe_locate_on_screen(oversized, 0.9, self.region))

    def test_field_search_continues_after_template_exceeds_region(self):
        oversized = Image.new("RGB", (60, 20), "black")
        with (
            patch.object(utils, "get_gw_screen", return_value=self.region),
            patch.object(actions.config, "fieldStep1", oversized),
            patch.object(actions.config, "fieldStep2", self.needle),
            patch("pyscreeze.screenshot", return_value=self.screen) as screenshot,
        ):
            result = actions.get_actual_field()

        self.assertEqual(result, {"field": "ar_field_step_2", "box": (20, 15, 30, 20)})
        self.assertEqual(screenshot.call_count, 2)

    def test_missing_or_invalid_region_does_not_search_entire_screen(self):
        regions = [None, (0, 0, 0, 40), (0, 0, 40, 0), (0, 0, -1, 40), (0, 0, 40, -1)]
        for region in regions:
            with (
                self.subTest(region=region),
                patch.object(utils, "get_gw_screen", return_value=region),
                patch.object(actions.pyautogui, "locateOnScreen") as locate,
            ):
                self.assertEqual(actions.get_actual_field(), "unknown")
                locate.assert_not_called()

    def test_minimized_game_window_has_no_capture_region(self):
        window = SimpleNamespace(
            left=-32000, top=-32000, width=160, height=28, isMinimized=True,
        )
        with patch.object(utils.gw, "getWindowsWithTitle", return_value=[window]):
            self.assertIsNone(utils.get_gw_screen())

    def test_restored_window_is_used_after_a_minimized_window(self):
        minimized = SimpleNamespace(
            left=-32000, top=-32000, width=160, height=28, isMinimized=True,
        )
        restored = SimpleNamespace(
            left=100, top=200, width=1280, height=720, isMinimized=False,
        )
        with patch.object(utils.gw, "getWindowsWithTitle", return_value=[minimized, restored]):
            self.assertEqual(utils.get_gw_screen(), (100, 200, 1280, 720))

    def test_game_window_with_invalid_dimensions_has_no_capture_region(self):
        for width, height in ((0, 400), (600, 0), (-1, 400), (600, -1)):
            window = SimpleNamespace(
                left=0, top=0, width=width, height=height, isMinimized=False,
            )
            with (
                self.subTest(width=width, height=height),
                patch.object(utils.gw, "getWindowsWithTitle", return_value=[window]),
            ):
                self.assertIsNone(utils.get_gw_screen())

    def test_unexpected_value_error_is_not_hidden(self):
        with patch.object(
            actions.pyautogui, "locateOnScreen", side_effect=ValueError("invalid confidence"),
        ):
            with self.assertRaisesRegex(ValueError, "invalid confidence"):
                actions.safe_locate_on_screen(self.needle, 0.9, self.region)

    def test_normal_match_returns_absolute_box(self):
        with patch("pyscreeze.screenshot", return_value=self.screen):
            box = actions.safe_locate_on_screen(self.needle, 0.9, self.region)

        self.assertEqual(box, (20, 15, 30, 20))


if __name__ == "__main__":
    unittest.main()
