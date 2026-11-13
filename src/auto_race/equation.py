"""Representa e valida a soma lida de uma imagem."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Addition:
    left: int
    right: int

    def __post_init__(self) -> None:
        for name, value in (("left", self.left), ("right", self.right)):
            if type(value) is not int:
                raise TypeError(f"{name} deve ser um inteiro nativo")
            if not 0 <= value <= 99:
                raise ValueError(f"{name} deve estar entre 0 e 99")

    @property
    def result(self) -> int:
        return self.left + self.right


def parse_addition(text: str) -> Addition | None:
    """Aceita apenas dois operandos completos separados por um sinal de soma."""
    if not isinstance(text, str):
        return None
    match = re.fullmatch(r"([0-9]{1,2})[ \t]*\+[ \t]*([0-9]{1,2})(?:[ \t]*=)?", text.strip())
    if match is None:
        return None
    return Addition(int(match.group(1)), int(match.group(2)))
