import os
import sys
import math
import random
import time
import pygetwindow as gw
import pyautogui
import numpy as np
import cv2
import keyboard


def human_move_to(x, y=None):
    """Move em curva, com velocidade variada, mantendo o destino exato."""
    if y is None:
        x, y = x
    x, y = int(x), int(y)
    start_x, start_y = pyautogui.position()
    dx, dy = x - start_x, y - start_y
    distance = math.hypot(dx, dy)
    if distance == 0:
        return

    duration = (random.uniform(0.18, 0.30) + min(distance / 1600, 0.60)) * 0.75
    bend = random.uniform(-1, 1) * min(distance * 0.18, 80)
    midpoint = random.uniform(0.35, 0.65)
    control_x = start_x + dx * midpoint - dy / distance * bend
    control_y = start_y + dy * midpoint + dx / distance * bend
    width, height = pyautogui.size()
    control_x = max(min(0, start_x, x), min(max(width - 1, start_x, x), control_x))
    control_y = max(min(0, start_y, y), min(max(height - 1, start_y, y), control_y))

    steps = max(12, int(duration * 60))
    started_at = time.perf_counter()
    for step in range(1, steps + 1):
        progress = step / steps
        t = progress * progress * (3 - 2 * progress)
        inverse = 1 - t
        next_x = inverse ** 2 * start_x + 2 * inverse * t * control_x + t ** 2 * x
        next_y = inverse ** 2 * start_y + 2 * inverse * t * control_y + t ** 2 * y
        pyautogui.moveTo(round(next_x), round(next_y), _pause=False)
        delay = started_at + duration * progress - time.perf_counter()
        if delay > 0:
            time.sleep(delay)


def human_click(x, y=None, *, jitter=0):
    """Chega ao alvo suavemente, com desvio opcional e pausas variadas."""
    if jitter:
        if y is None:
            x, y = x
        x += random.randint(-jitter, jitter)
        y += random.randint(-jitter, jitter)
    human_move_to(x, y)
    time.sleep(random.uniform(0.06, 0.16))
    pyautogui.click(_pause=False)
    time.sleep(random.uniform(0.08, 0.20))


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

def resolve_equation(origin=None):
    try:
        mouse_x, mouse_y = pyautogui.position() if origin is None else origin
        num1 = extract_number_from_region((mouse_x - 175, mouse_y - 20, 40, 40))
        num2 = extract_number_from_region((mouse_x - 125, mouse_y - 20, 40, 40))

        if num1 is not None and num2 is not None:
            resultado = num1 + num2
            print(f"[OCR] Resultado: {num1} + {num2} = {resultado}")
            for digit in str(resultado):
                keyboard.press_and_release(digit)
            human_click(mouse_x + 265, mouse_y + 110)
        else:
            print("[OCR] Não foi possível extrair ambos os números corretamente.")
    except Exception as e:
        print("[OCR] Erro ao tentar resolver a equação:", e)
        return False
