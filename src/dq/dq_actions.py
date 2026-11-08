
import pyautogui 
from src import actions
from src import config
from pyautogui import ImageNotFoundException, sleep


def do_dq_125_daily(box):
    centro = pyautogui.center(box)
    pyautogui.moveTo(centro.x - 180, centro.y + 60)
    pyautogui.click()
    # sleep(1)
    # actions.do_press_btn_accept()
    # actions.do_press_btn_finish()

def do_dq_gems_daily(box):
    centro = pyautogui.center(box)
    pyautogui.moveTo(centro.x - 180, centro.y + 60)
    pyautogui.click()
    # sleep(1)
    actions.do_press_btn_accept()
    # actions.do_press_btn_finish()