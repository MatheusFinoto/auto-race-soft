import keyboard
import time
import threading
from src import actions

exit_flag = threading.Event()

def monitor_esc():
    keyboard.wait('esc')
    exit_flag.set()
    print("ESC pressionado. Finalizando script...")

def executar_script():
    threading.Thread(target=monitor_esc, daemon=True).start()
    
    while not exit_flag.is_set():
        current_field = actions.get_actual_field()

        if current_field != "unknown":
            actions.switch_field_action(current_field)

print("Script de automação iniciado em loop infinito.")
print("Pressione 'ESC' para parar a qualquer momento.")
executar_script()
# # Configura o hotkey: toda vez que a tecla 'a' for pressionada, a função executar_script é chamada
# keyboard.add_hotkey('a',executar_script)