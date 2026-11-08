import sys
import threading

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", line_buffering=True)

import keyboard
from src import actions, config

exit_flag = threading.Event()

def monitor_esc():
    keyboard.wait('esc')
    exit_flag.set()
    print("ESC pressionado. Finalizando script...")

def executar_script():
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

if __name__ == "__main__":
    print("Script de automação iniciado em loop infinito.")
    print("Pressione 'ESC' para parar a qualquer momento.")
    executar_script()
