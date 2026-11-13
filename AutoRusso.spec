# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

project_root = Path(SPECPATH)
tesseract_root = Path(os.environ.get('TESSERACT_DIR', r'C:\Program Files\Tesseract-OCR'))
for required in ('tesseract.exe', 'tessdata/eng.traineddata'):
    if not (tesseract_root / required).is_file():
        raise FileNotFoundError(f'Tesseract necessario para o build: {tesseract_root / required}')

tesseract_binaries = [(str(tesseract_root / 'tesseract.exe'), 'tesseract')]
tesseract_binaries += [(str(path), 'tesseract') for path in sorted(tesseract_root.glob('*.dll'))]

# O reconhecimento usa apenas o modelo padrão; os modelos beta e de detecção
# permanecem fora do pacote. O hook do onnxruntime coleta suas DLLs.
local_ocr_models = collect_data_files('ddddocr', includes=['common_old.onnx'])
if len(local_ocr_models) != 1:
    raise FileNotFoundError('Modelo de OCR local common_old.onnx nao encontrado. Instale requirements.txt.')

a = Analysis(
    [str(project_root / 'src' / 'main.py')],
    pathex=[str(project_root)],
    binaries=tesseract_binaries,
    datas=[
        (str(project_root / 'images'), 'images'),
        (str(tesseract_root / 'tessdata' / 'eng.traineddata'), 'tesseract/tessdata'),
        *local_ocr_models,
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AutoRusso',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
