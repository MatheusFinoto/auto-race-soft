"""Gera o executável e o lançador que troca seu nome em cada abertura."""

import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT / "dist" / "AutoRusso"
APP = PACKAGE / "app"


def main():
    if importlib.util.find_spec("PyInstaller") is None:
        raise SystemExit(
            "Instale o empacotador: python -m pip install -r requirements-build.txt"
        )

    if not APP.resolve().is_relative_to(ROOT):
        raise RuntimeError("A pasta de build deve permanecer dentro do projeto.")
    APP.mkdir(parents=True, exist_ok=True)
    for artifact in APP.glob("*.exe"):
        if artifact.resolve().parent != APP.resolve():
            raise RuntimeError(f"Executavel fora da pasta de build: {artifact}")
        if not re.fullmatch(r"AutoRusso|[0-9a-f]{32}", artifact.stem):
            raise RuntimeError(f"Arquivo desconhecido na pasta do build: {artifact.name}")
        try:
            artifact.unlink()
        except PermissionError as error:
            raise SystemExit("Feche a instancia do programa antes de gerar outro build.") from error

    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
            "--distpath", str(APP), "--workpath", str(ROOT / "build" / "package"),
            str(ROOT / "AutoRusso.spec"),
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run([str(APP / "AutoRusso.exe"), "--check-build"], cwd=PACKAGE, check=True)
    shutil.copy2(ROOT / "packaging" / "Iniciar.cmd", PACKAGE / "Iniciar.cmd")
    archive = shutil.make_archive(str(PACKAGE), "zip", root_dir=PACKAGE.parent, base_dir=PACKAGE.name)
    print(f"\nBuild pronto. Abra: {PACKAGE / 'Iniciar.cmd'}")
    print(f"Pacote para distribuir: {archive}")


if __name__ == "__main__":
    main()
