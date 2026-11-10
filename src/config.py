import os

from src.utils import get_resource_path

TESSERACT_PATH = get_resource_path("tesseract")
if not os.path.isfile(os.path.join(TESSERACT_PATH, "tesseract.exe")):
    TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR"

# Configurações gerais do projeto

# Caminho para a pasta de imagens
IMAGES_PATH = "images/"
NPC_PATH = "npcs/"

# btns
btnOk = get_resource_path(IMAGES_PATH+'btn_ok.png')
btnSearch = get_resource_path(IMAGES_PATH+'btn_search.png')
btnFinish = get_resource_path(IMAGES_PATH+'btn_finish.png')
btnAccept = get_resource_path(IMAGES_PATH+'btn_accept.png')

# fields
logo = get_resource_path(IMAGES_PATH+'logo.png')
fieldStep1 = get_resource_path(IMAGES_PATH+'fields/field_step_1.png')
fieldStep2 = get_resource_path(IMAGES_PATH+'fields/field_step_2.png')
fieldStep3 = get_resource_path(IMAGES_PATH+'fields/field_step_3.png')
fieldSuccess = get_resource_path(IMAGES_PATH+'fields/field_success.png')

#search
btnAthens = get_resource_path(IMAGES_PATH+'search/athens_label.png')
btnSearch = get_resource_path(IMAGES_PATH+'search/search_label.png')
btnSearchNpc1 = get_resource_path(IMAGES_PATH+'search/search_npc_1.png')
btnSearchNpc2 = get_resource_path(IMAGES_PATH+'search/search_npc_2.png')
btnSearchNpc3 = get_resource_path(IMAGES_PATH+'search/search_npc_3.png')
btnSearchNpc4 = get_resource_path(IMAGES_PATH+'search/search_npc_4.png')
btnSearchNpc5 = get_resource_path(IMAGES_PATH+'search/search_npc_5.png')

# DQ
dqThermo125Daily = get_resource_path(IMAGES_PATH+'dq_fields/dq_thermo_125_daily.png')
dqThermoGemsDaily = get_resource_path(IMAGES_PATH+'dq_fields/dq_thermo_gems_daily.png')


# Parâmetros de busca
CONFIDENCE = 0.9
WAIT_TIME = 0.2  # tempo em segundos antes de executar uma ação
