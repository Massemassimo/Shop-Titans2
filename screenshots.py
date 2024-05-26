from PIL import Image, ImageDraw, ImageFont
import pyautogui
from globals import *
import subprocess
import sys
import datetime
import cv2

def takeScreenshot(regionFind = [0,0,0,0]):
    
    screenshot = pyautogui.screenshot()
    draw = ImageDraw.Draw(screenshot)

    distance_x = 100
    distance_y = 100
    display_width = 2560
    display_height = 1440

    # Wählen Sie eine Schriftart für die Beschriftung
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    # Zeichne horizontale Linien und beschrifte sie
    for i in range(distance_y, display_height, distance_y):
        draw.line([(0, i), (display_width, i)], fill="red", width=2)
        draw.text((10, i-25), str(i), fill="red", font=font)
        draw.text((display_width - 80, i-25), str(i), fill="red", font=font)

    # Zeichne vertikale Linien und beschrifte sie
    for i in range(distance_x, display_width, distance_x):
        draw.line([(i, 0), (i, display_height)], fill="red", width=2)
        draw.text((i-40, 10), str(i), fill="red", font=font)
        draw.text((i-40, display_height - 40), str(i), fill="red", font=font)
        x, y, width, height = regionFind
        draw.rectangle([x, y, x + width, y + height], outline="lawngreen", width=5)

    # Erstellen eines eindeutigen Dateinamens basierend auf dem aktuellen Zeitstempel
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S%f")
    screenshot_path = f"debugScreens/debug_screenshot-{timestamp}.png"
    screenshot.save(screenshot_path)
    # # Öffne den Screenshot mit dem Standardbildbetrachter des Systems
    # subprocess.run(["open", screenshot_path], check=True if sys.platform == 'darwin' else subprocess.run(["start", screenshot_path], shell=True))
    return screenshot_path


def takeAndShowScreenshot(regionFind = [0,0,0,0]):
    screenshot_path = takeScreenshot(regionFind)
    subprocess.run(["start", screenshot_path], shell=True, check=True)