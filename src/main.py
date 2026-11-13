import sys
import threading

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", line_buffering=True)

import keyboard
from src import actions, config, utils

exit_flag = threading.Event()

def monitor_esc():
    keyboard.wait('esc')
    exit_flag.set()
    print("ESC pressionado. Finalizando script...")

def executar_script():
    try:
        utils.prepare_number_reader()
    except (ValueError, RuntimeError) as error:
        raise SystemExit(f"[Configuração] {error}") from None
    threading.Thread(target=monitor_esc, daemon=True).start()
    waiting_for_field = False
    
    while not exit_flag.is_set():
        current_field = actions.get_actual_field()

        if current_field != "unknown":
            waiting_for_field = False
            print(f"[Tela] Reconhecida: {current_field['field']}")
            actions.switch_field_action(current_field)
        elif not waiting_for_field:
            print("[Aguardando] Nenhuma tela reconhecida. Deixe o jogo visível na tela da corrida ou missão diária.")
            waiting_for_field = True

        exit_flag.wait(config.WAIT_TIME)

def check_build():
    """Valida imports, imagens e OCR sem iniciar a automação."""
    from pathlib import Path

    if not utils.AWNSERS_CACHE:
        raise RuntimeError("Templates de numeros nao encontrados.")
    tesseract = Path(config.TESSERACT_PATH) / "tesseract.exe"
    if not (tesseract.parent / "tessdata" / "eng.traineddata").is_file():
        raise FileNotFoundError("Dados de OCR nao encontrados.")
    utils.pytesseract.pytesseract.tesseract_cmd = str(tesseract)
    version = utils.pytesseract.get_tesseract_version()
    from PIL import Image
    from src.auto_race.local_reader import LocalEquationReader

    # Carrega os pesos e as DLLs também no executável, sem interagir com o jogo.
    LocalEquationReader().read_equation(Image.new("L", (100, 40), 255))
    print(f"Executavel: {Path(sys.executable).name}")
    print(f"Build OK: OCR local carregado; {len(utils.AWNSERS_CACHE)} templates; Tesseract {version}.")


if __name__ == "__main__":
    if "--check-build" in sys.argv[1:]:
        check_build()
    else:
        print("Script de automação iniciado em loop infinito.")
        print("Pressione 'ESC' para parar a qualquer momento.")
        executar_script()
