import pyautogui
from src import config
from src.utils import get_gw_screen, human_click

def do_press_btn_ok():
    try:
        lBtnOk = pyautogui.locateOnScreen(config.btnOk, confidence=config.CONFIDENCE)
        if lBtnOk:
            centro = pyautogui.center(lBtnOk)
            human_click(centro)
        else:
            print("[UI] Botão 'OK' não encontrado na tela.")
    except Exception as e:
        print("[Erro] Erro ao localizar botão OK:", e)

def do_press_btn_search():
    try:
        lBtnSearch = pyautogui.locateOnScreen(config.btnSearch, confidence=config.CONFIDENCE)
        if lBtnSearch:
            centro = pyautogui.center(lBtnSearch)
            human_click(centro)
        else:
            print("[UI] Botão 'Search' não encontrado na tela.")
    except Exception as e:
        print("[Erro] Erro ao localizar botão Search:", e)

def do_press_btn_finish():
    try:
        lBtnOk = pyautogui.locateOnScreen(config.btnFinish, confidence=config.CONFIDENCE, region=get_gw_screen())
        if lBtnOk:
            centro = pyautogui.center(lBtnOk)
            human_click(centro)
        else:
            print("[UI] Botão 'FINISH' não encontrado na tela.")
    except Exception as e:
        print("[Erro] Erro ao localizar botão FINISH:", e)

def do_press_btn_accept():
    try:
        lBtnOk = pyautogui.locateOnScreen(config.btnAccept, confidence=config.CONFIDENCE, region=get_gw_screen())
        if lBtnOk:
            centro = pyautogui.center(lBtnOk)
            human_click(centro)
        else:
            print("[UI] Botão 'ACCEPT' não encontrado na tela.")
    except Exception as e:
        print("[Erro] Erro ao localizar botão ACCEPT:", e)
