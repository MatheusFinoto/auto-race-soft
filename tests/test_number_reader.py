from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image, ImageDraw

from src.auto_race.number_reader import DigitTemplateBank


TEMPLATES = Path(__file__).resolve().parents[1] / "images" / "awnsers"


def composed_number():
    image = Image.new("RGB", (40, 40), (25, 55, 85))
    for digit, left in ((9, 13), (7, 20)):
        with Image.open(TEMPLATES / f"{digit}.png") as template:
            image.paste(template.crop((13, 9, 19, 18)), (left, 9))
    return image


class DigitTemplateBankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = DigitTemplateBank(TEMPLATES)

    def test_reads_all_distributed_number_images(self):
        paths = sorted(TEMPLATES.glob("*.png"))
        self.assertEqual(len(paths), 98)
        for path in paths:
            with self.subTest(number=path.stem), Image.open(path) as image:
                self.assertEqual(self.bank.read_number(image), int(path.stem))

    def test_reads_unseen_number_with_different_background(self):
        self.assertFalse((TEMPLATES / "97.png").exists())
        self.assertEqual(self.bank.read_number(composed_number()), 97)

    def test_ignores_dialog_border_outside_number_text(self):
        image = composed_number()
        ImageDraw.Draw(image).rectangle((0, 0, 39, 39), outline="white", width=4)

        self.assertEqual(self.bank.read_number(image), 97)

    def test_rejects_ambiguous_glyph(self):
        with TemporaryDirectory() as directory:
            with Image.open(TEMPLATES / "9.png") as image:
                image.save(Path(directory) / "1.png")
                image.save(Path(directory) / "7.png")
                bank = DigitTemplateBank(directory)
                self.assertIsNone(bank.read_number(image))

    def test_rejects_unknown_glyph_without_returning_partial_number(self):
        with TemporaryDirectory() as directory:
            with Image.open(TEMPLATES / "9.png") as template:
                template.save(Path(directory) / "9.png")
            bank = DigitTemplateBank(directory)
            unknown = Image.new("RGB", (40, 40), "black")
            draw = ImageDraw.Draw(unknown)
            draw.line((13, 9, 18, 17), fill="white")
            draw.line((18, 9, 13, 17), fill="white")
            self.assertIsNone(bank.read_number(unknown))

            mixed = composed_number()
            draw = ImageDraw.Draw(mixed)
            draw.rectangle((20, 9, 25, 17), fill="black")
            draw.line((20, 9, 25, 17), fill="white")
            draw.line((25, 9, 20, 17), fill="white")
            self.assertIsNone(bank.read_number(mixed))

    def test_blank_image_and_missing_templates_have_no_number(self):
        self.assertIsNone(self.bank.read_number(Image.new("RGB", (40, 40), "black")))
        with TemporaryDirectory() as directory:
            bank = DigitTemplateBank(directory)
            self.assertIsNone(bank.read_number(composed_number()))


if __name__ == "__main__":
    unittest.main()
