"""Reconhecimento de somas com modelo ONNX executado somente na CPU local."""

from dataclasses import dataclass
from itertools import groupby

import cv2
import numpy as np
from PIL import Image, ImageOps

from src.auto_race.equation import Addition, parse_addition


class LocalReadError(RuntimeError):
    """Falha ao carregar ou executar o modelo de reconhecimento local."""


@dataclass(frozen=True)
class _Reading:
    addition: Addition
    confidence: float


def _decode_prediction(payload: dict) -> _Reading | None:
    """Decodifica CTC sem descartar letras ou inventar o sinal de soma."""
    charset = payload.get("charset")
    if not isinstance(charset, list) or not charset or charset[0] != "":
        raise LocalReadError("O modelo local devolveu um alfabeto inválido.")
    try:
        probabilities = np.asarray(payload["probabilities"], dtype=np.float32)
    except (KeyError, TypeError, ValueError) as error:
        raise LocalReadError("O modelo local devolveu probabilidades inválidas.") from error
    if probabilities.ndim == 3 and probabilities.shape[1] == 1:
        probabilities = probabilities[:, 0, :]
    elif probabilities.ndim == 3 and probabilities.shape[0] == 1:
        probabilities = probabilities[0, :, :]
    if (
        probabilities.ndim != 2
        or probabilities.shape[1] != len(charset)
        or probabilities.shape[0] == 0
        or not np.isfinite(probabilities).all()
        or (probabilities < 0).any()
        or (probabilities > 1).any()
    ):
        raise LocalReadError("O modelo local devolveu probabilidades inválidas.")

    characters = []
    confidences = []
    indices = probabilities.argmax(axis=1)
    for index, steps in groupby(range(len(indices)), key=lambda step: int(indices[step])):
        if index == 0:
            continue
        steps = list(steps)
        best_step = max(steps, key=lambda step: float(probabilities[step, index]))
        row = probabilities[best_step]
        confidence = float(row[index])
        runner_up = float(np.partition(row, -2)[-2])
        # Mede cada caractere emitido; a média do pacote inclui os blanks CTC.
        if confidence < 0.65 or confidence - runner_up < 0.20:
            return None
        character = charset[index]
        if character not in "0123456789+=":
            return None
        characters.append(character)
        confidences.append(confidence)
    addition = parse_addition("".join(characters))
    return _Reading(addition, min(confidences)) if addition is not None else None


def _image_variants(image: Image.Image) -> list[Image.Image]:
    image = ImageOps.exif_transpose(image)
    if image.width < 8 or image.height < 8:
        return []
    if image.width > 4096 or image.height > 4096:
        raise LocalReadError("Recorte a imagem da soma para no máximo 4096 × 4096 pixels.")
    if image.mode in ("RGBA", "LA") or "transparency" in image.info:
        rgba = image.convert("RGBA")
        image = Image.alpha_composite(Image.new("RGBA", rgba.size, "white"), rgba)
    gray = np.array(image.convert("L"))
    if int(gray.max()) - int(gray.min()) < 20:
        return []
    # O modelo espera texto escuro, incluindo quando o jogo usa fundo escuro.
    if np.median(gray) < 128:
        gray = 255 - gray
    # Retira apenas uma moldura contínua detectada nas quatro bordas.
    threshold = float(np.median(gray)) - 40
    edges = (gray[0], gray[-1], gray[:, 0], gray[:, -1])
    if all(float(np.mean(edge < threshold)) > 0.8 for edge in edges):
        gray = gray[1:-1, 1:-1]
    denoised = cv2.medianBlur(gray, 3)
    contrasted = np.asarray(ImageOps.autocontrast(Image.fromarray(denoised)))
    variants = []
    seen = set()
    scale = min(6.0, 1024 / max(gray.shape))
    for pixels in (gray, denoised, contrasted):
        prepared = Image.fromarray(pixels).resize(
            (max(1, round(pixels.shape[1] * scale)), max(1, round(pixels.shape[0] * scale))),
            Image.Resampling.BICUBIC,
        )
        prepared = ImageOps.expand(prepared, border=max(4, round(4 * scale)), fill=255)
        signature = (prepared.size, prepared.tobytes())
        if signature not in seen:
            variants.append(prepared)
            seen.add(signature)
    return variants


class LocalEquationReader:
    """Reutiliza um modelo local e rejeita leituras incertas ou divergentes."""

    def __init__(self, engine=None):
        if engine is None:
            try:
                import onnxruntime
                from ddddocr import DdddOcr

                # Os pesos vêm no pacote instalado; não há download na leitura.
                onnxruntime.disable_telemetry_events()
                engine = DdddOcr(show_ad=False, use_gpu=False)
            except ImportError as error:
                raise LocalReadError(
                    "Instale o leitor local: python -m pip install -r requirements.txt"
                ) from error
            except Exception as error:
                raise LocalReadError("Não foi possível carregar o modelo de OCR local.") from error
        self._engine = engine

    def read_equation(self, image: Image.Image) -> Addition | None:
        variants = _image_variants(image)
        if not variants:
            return None
        readings = []
        for variant in variants:
            try:
                payload = self._engine.classification(variant, probability=True)
            except Exception as error:
                raise LocalReadError("Falha ao executar o modelo de OCR local.") from error
            if not isinstance(payload, dict):
                raise LocalReadError("O modelo local devolveu uma resposta inválida.")
            reading = _decode_prediction(payload)
            if reading is not None:
                readings.append(reading)
        if not readings:
            return None
        if any(reading.addition != readings[0].addition for reading in readings[1:]):
            return None
        if len(readings) < 2 and readings[0].confidence < 0.85:
            return None
        return readings[0].addition
