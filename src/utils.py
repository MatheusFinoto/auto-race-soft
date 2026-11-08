import os
import sys
import pygetwindow as gw
import pyautogui
import numpy as np
import cv2
import keyboard


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller: caminho temporário do pacote
        return os.path.join(sys._MEIPASS, relative_path)
    # Desenvolvimento: raiz do projeto
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

def get_gw_screen():
    windows = gw.getWindowsWithTitle("Godsarena Online")
    if windows:
        window = windows[0]
        return (window.left, window.top, window.width, window.height)
    else:
        print("[Janela] Janela GodsWar não encontrada.")
        return None
    
# Cache das imagens de referência
AWNSERS_CACHE = []

def load_awnsers_images():
    """Carrega todas as imagens de referência em memória."""
    awnsers_dir = os.path.join(os.path.dirname(__file__), '..', 'images', 'awnsers')
    awnsers_dir = get_resource_path(awnsers_dir)
    cache = []
    for filename in os.listdir(awnsers_dir):
        if filename.endswith('.png'):
            num_str = filename.split('.')[0]
            ref_img_path = os.path.join(awnsers_dir, filename)
            ref_img = cv2.imread(ref_img_path, cv2.IMREAD_GRAYSCALE)
            if ref_img is not None:
                cache.append((int(num_str), ref_img))
            else:
                print(f"[Imagem] Erro ao carregar {filename}")
    return cache

# Inicializa o cache ao carregar o módulo
AWNSERS_CACHE = load_awnsers_images()
    
def extract_number_from_region(region, scale_percent=400):
    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    width = int(gray.shape[1] * scale_percent / 100)
    height = int(gray.shape[0] * scale_percent / 100)
    resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LINEAR)

    best_score = 0
    best_num = None

    for num, ref_img in AWNSERS_CACHE:
        try:
            ref_img_resized = cv2.resize(ref_img, (resized.shape[1], resized.shape[0]), interpolation=cv2.INTER_LINEAR)
            score = cv2.matchTemplate(resized, ref_img_resized, cv2.TM_CCOEFF_NORMED).max()
            if score > best_score:
                best_score = score
                best_num = num
        except Exception as e:
            print(f"[Imagem] Erro ao comparar número {num}: {e}")

    # Considera match apenas se score for maior que 80%
    if best_score > 0.8:
        return best_num
    else:
        print(f"[Imagem] Nenhuma correspondência forte encontrada. Score máximo: {best_score}")
        return None

def resolve_equation():
    try:
        mouse_x, mouse_y = pyautogui.position()
        num1 = extract_number_from_region((mouse_x - 175, mouse_y - 20, 40, 40))
        num2 = extract_number_from_region((mouse_x - 125, mouse_y - 20, 40, 40))

        if num1 is not None and num2 is not None:
            resultado = num1 + num2
            print(f"[OCR] Resultado: {num1} + {num2} = {resultado}")
            for digit in str(resultado):
                keyboard.press_and_release(digit)
            pyautogui.moveTo(mouse_x + 265, mouse_y + 110)
            pyautogui.click()
        else:
            print("[OCR] Não foi possível extrair ambos os números corretamente.")
    except Exception as e:
        print("[OCR] Erro ao tentar resolver a equação:", e)
        return False