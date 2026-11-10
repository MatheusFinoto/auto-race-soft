import pyautogui
from src import utils

def do_ar_step_1(box):
    centro = pyautogui.center(box)
    utils.human_click(centro.x - 170, centro.y - 45, jitter=2)
    print("[Step] SUCESSO STEP 1")

def do_ar_step_2(box):
    centro = pyautogui.center(box)
    utils.human_click(centro.x - 170, centro.y,)
    utils.human_click(centro.x - 170, centro.y,)
    # utils.human_click(centro.x + 170, centro.y + 120)
    print("[Step] SUCESSO STEP 2")

def do_ar_step_3(box):
    ponto_clique = (box.left + 198, box.top + 153)
    utils.human_click(ponto_clique, jitter=2)
    if not utils.resolve_equation(origin=ponto_clique):
        return False
    print("[Step] SUCESSO STEP 3")
    return True
