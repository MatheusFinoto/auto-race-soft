import pyautogui
from src import config, utils
from pyautogui import ImageNotFoundException

from src.auto_race import auto_race
from src.dq import dq_actions
from src.buttons import buttons


def get_actual_field():
    region = utils.get_gw_screen()
    confidence = config.CONFIDENCE
    fields = [
        # Campos de Auto Race
        ("ar_field_step_1", config.fieldStep1),
        ("ar_field_step_2", config.fieldStep2),
        ("ar_field_step_3", config.fieldStep3),
        # Campos de DQ
        ("dq_thermo_125_daily", config.dqThermo125Daily),
        ("dq_thermo_gems_daily", config.dqThermoGemsDaily),
        # Buttons
        ("btn_accept", config.btnAccept),
        ("btn_finish", config.btnFinish),
    ]

    for field_name, image in fields:
        box = safe_locate_on_screen(image, confidence, region)
        if box:
            return {'field': field_name, 'box': box}

    return "unknown"

def switch_field_action(ar_field):
    # Ações de Auto Race
    if ar_field['field'] == "ar_field_step_1":
        return auto_race.do_ar_step_1(ar_field['box'])
    elif ar_field['field'] == "ar_field_step_2":
        return auto_race.do_ar_step_2(ar_field['box'])
    #elif ar_field['field'] == "ar_field_step_3":
    #    return auto_race.do_ar_step_3(ar_field['box'])
    # DQ Actions
    elif ar_field['field'] == "dq_thermo_125_daily":
        return dq_actions.do_dq_125_daily(ar_field['box'])
    elif ar_field['field'] == "dq_thermo_gems_daily":
        return dq_actions.do_dq_gems_daily(ar_field['box'])
    # Buttons
    elif ar_field['field'] == "btn_accept":
        return buttons.do_press_btn_accept()
    elif ar_field['field'] == "btn_finish":
        return buttons.do_press_btn_finish()
    else:
        print(f"[Erro] Campo desconhecido: {ar_field['field']}")
        return False

def safe_locate_on_screen(image, confidence, region):
    try:
        return pyautogui.locateOnScreen(image, confidence=confidence, region=region)
    except ImageNotFoundException:
        return None