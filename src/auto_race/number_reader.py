"""Reconhece os dígitos da soma usando os templates existentes."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def _extract_glyphs(image: Image.Image) -> list[np.ndarray]:
    # Região do texto dentro de cada captura 40x40; exclui fundo e moldura.
    pixels = np.asarray(image.convert("RGB"))[4:20, 8:32]
    if pixels.size == 0:
        return []
    minimum = pixels.min(axis=2)
    mask = np.where(
        (minimum > 100) & (pixels.max(axis=2) - minimum < 55),
        255,
        0,
    ).astype(np.uint8)

    glyphs = []
    start = None
    occupied_columns = (mask > 0).any(axis=0).tolist()
    for column, occupied in enumerate([*occupied_columns, False]):
        if occupied and start is None:
            start = column
        elif not occupied and start is not None:
            glyph = mask[:, start:column]
            rows, columns = np.where(glyph > 0)
            glyphs.append(
                glyph[rows.min():rows.max() + 1, columns.min():columns.max() + 1]
            )
            start = None
    return glyphs


def _glyph_vector(glyph: np.ndarray) -> np.ndarray:
    resized = cv2.resize(glyph, (24, 32), interpolation=cv2.INTER_LINEAR)
    vector = resized.astype(np.float32).reshape(-1)
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm > 1e-8 else np.zeros_like(vector)


class DigitTemplateBank:
    """Separa e compara dígitos como o leitor do projeto de referência."""

    def __init__(self, templates_directory: str | Path):
        self._digits = []
        vectors = []
        for path in sorted(Path(templates_directory).glob("*.png")):
            if not path.stem.isdigit():
                continue
            with Image.open(path) as image:
                glyphs = _extract_glyphs(image)
            if len(glyphs) != len(path.stem):
                continue
            for digit, glyph in zip(path.stem, glyphs):
                self._digits.append(digit)
                vectors.append(_glyph_vector(glyph))
        self._vectors = np.stack(vectors) if vectors else np.empty((0, 768))

    def read_number(self, image: Image.Image) -> int | None:
        glyphs = _extract_glyphs(image)
        if not glyphs or not self._digits:
            return None

        digits = []
        for glyph in glyphs:
            scores = self._vectors @ _glyph_vector(glyph)
            scores_by_digit = {}
            for digit, score in zip(self._digits, scores):
                scores_by_digit[digit] = max(
                    scores_by_digit.get(digit, -1.0), float(score)
                )
            ranked = sorted(scores_by_digit.values(), reverse=True)
            best_digit = max(scores_by_digit, key=scores_by_digit.get)
            # Exige confiança e diferença suficiente para o segundo candidato.
            if ranked[0] < 0.80 or (len(ranked) > 1 and ranked[0] - ranked[1] < 0.015):
                return None
            digits.append(best_digit)
        return int("".join(digits))
