"""Testa a leitura de somas em arquivos, sem iniciar a automação do jogo."""

import argparse
from pathlib import Path
import sys

from PIL import Image

from src.auto_race.local_reader import LocalEquationReader, LocalReadError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", metavar="imagem", type=Path, nargs="+")
    parser.add_argument(
        "--crop",
        metavar=("ESQUERDA", "TOPO", "LARGURA", "ALTURA"),
        type=int,
        nargs=4,
        help="Lê somente este recorte da imagem, em pixels.",
    )
    arguments = parser.parse_args(argv)
    if arguments.crop is not None:
        left, top, width, height = arguments.crop
        if left < 0 or top < 0 or width <= 0 or height <= 0:
            parser.error("--crop exige esquerda/topo não negativos e largura/altura positivas.")

    try:
        reader = LocalEquationReader()
    except LocalReadError as error:
        print(f"[OCR local] {error}", file=sys.stderr)
        return 1

    failed = False
    for path in arguments.images:
        try:
            with Image.open(path) as source:
                if arguments.crop is not None:
                    left, top, width, height = arguments.crop
                    if left + width > source.width or top + height > source.height:
                        print(f"{path}: o recorte ultrapassa os limites da imagem.", file=sys.stderr)
                        failed = True
                        continue
                    image = source.crop((left, top, left + width, top + height))
                else:
                    image = source.copy()
            equation = reader.read_equation(image)
        except (OSError, Image.DecompressionBombError):
            print(f"{path}: não foi possível abrir a imagem.", file=sys.stderr)
            failed = True
            continue
        except LocalReadError as error:
            print(f"{path}: {error}", file=sys.stderr)
            failed = True
            continue

        if equation is None:
            print(f"{path}: não foi possível ler a soma com segurança.", file=sys.stderr)
            failed = True
        else:
            print(f"{path}: {equation.left} + {equation.right} = {equation.result}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
