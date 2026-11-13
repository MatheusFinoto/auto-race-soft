from dataclasses import FrozenInstanceError
import unittest

from src.auto_race.equation import Addition, parse_addition


class AdditionTest(unittest.TestCase):
    def test_computes_result_at_operand_boundaries(self):
        for left, right, result in ((0, 0, 0), (0, 99, 99), (99, 99, 198)):
            with self.subTest(left=left, right=right):
                self.assertEqual(Addition(left, right).result, result)

    def test_operands_are_immutable(self):
        addition = Addition(26, 40)
        with self.assertRaises(FrozenInstanceError):
            addition.left = 99

    def test_rejects_operands_that_are_not_native_integers(self):
        class IntegerSubclass(int):
            pass

        for invalid in (True, False, 1.0, "1", None, IntegerSubclass(1)):
            with self.subTest(value=invalid):
                with self.assertRaises(TypeError):
                    Addition(invalid, 1)
                with self.assertRaises(TypeError):
                    Addition(1, invalid)

    def test_rejects_out_of_range_operands(self):
        for invalid in (-1, 100):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    Addition(invalid, 1)
                with self.assertRaises(ValueError):
                    Addition(1, invalid)


class ParseAdditionTest(unittest.TestCase):
    def test_reads_five_example_transcriptions(self):
        for text, left, right, result in (
            ("26+40", 26, 40, 66),
            ("62+2", 62, 2, 64),
            ("23+46", 23, 46, 69),
            ("78+43", 78, 43, 121),
            ("29+31", 29, 31, 60),
        ):
            with self.subTest(text=text):
                addition = parse_addition(text)
                self.assertEqual(addition, Addition(left, right))
                self.assertEqual(addition.result, result)

    def test_accepts_whitespace_and_an_optional_trailing_equals(self):
        for text in ("26 + 40", "26+40=", " 26 \t+\t 40 = ", "\n 26+40=\r\n"):
            with self.subTest(text=text):
                self.assertEqual(parse_addition(text), Addition(26, 40))

    def test_accepts_operand_boundaries_and_ascii_leading_zeroes(self):
        for text, expected in (
            ("0+99", Addition(0, 99)),
            ("99+0", Addition(99, 0)),
            ("00+09=", Addition(0, 9)),
        ):
            with self.subTest(text=text):
                self.assertEqual(parse_addition(text), expected)

    def test_rejects_incomplete_ambiguous_and_unrelated_content(self):
        for text in (
            "", " ", "26", "+40", "26+", "26 40", "2 6+40", "26+4 0",
            "26-40", "26*40", "26/40", "26++40", "26+40+2", "-26+40",
            "26+40=66", "26+40==", "=26+40", "100+2", "2+100", "000+1",
            "2.6+40", "O+40", "2b+40", "２６+４０", "٢٦+٤٠",
            "Soma: 26+40", "26+40 texto", "26\n+40", "26+\n40",
            "26+40\n=", "26+40\n29+31", "__import__('os')", None, 66,
        ):
            with self.subTest(text=text):
                self.assertIsNone(parse_addition(text))


if __name__ == "__main__":
    unittest.main()
