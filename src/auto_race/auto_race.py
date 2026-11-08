import pyautogui
from src import utils
from pyautogui import ImageNotFoundException

def do_ar_step_1(box):
    centro = pyautogui.center(box)
    utils.human_click(centro.x - 170, centro.y - 45)
    print("[Step] SUCESSO STEP 1")

def do_ar_step_2(box):
    centro = pyautogui.center(box)
    utils.human_click(centro.x - 170, centro.y)
    utils.human_click(centro.x + 170, centro.y + 120)
    print("[Step] SUCESSO STEP 2")

def do_ar_step_3(box):
    centro = pyautogui.center(box)
    utils.human_click(centro.x - 100, centro.y + 90)
    print("[Step] SUCESSO STEP 3")
    utils.resolve_equation()
