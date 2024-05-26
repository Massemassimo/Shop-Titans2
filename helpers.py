from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageGrab
import tesserocr
import pyautogui
import cv2
import numpy as np
from locators import locateAllOnScreenWithMask
from globals import *
from ocr import *
from screenshots import *
import re
import random
import cv2
import numpy as np
from PIL import Image
import tesserocr
import sys
import time
from collections import Counter


def clickRegion(region):
    pyautogui.click(pyautogui.center(region))
    pyautogui.sleep(0.5)
    
def sleepBetween(max=0.5, min=0.1):
    if min > max:
        raise ValueError("min darf nicht größer als max sein")

    # Generieren einer zufälligen Wartezeit zwischen min und max
    waitTime = random.uniform(min, max)
    
    # Warten für die generierte Zeit
    pyautogui.sleep(waitTime)
    
def findAndClick(imagePath, region=None, confidence=0.8, grayscale=False, debug = False):
    tries = 0
    while tries < 5:
        try:
            location = pyautogui.locateOnScreen(imagePath, region=region, confidence=confidence, grayscale=grayscale)
            if location:
                pyautogui.mouseDown(pyautogui.center(location))
                sleepBetween(0.2, 0.1)
                pyautogui.mouseUp(pyautogui.center(location))
                return True
            else:
                tries += 1
        except pyautogui.ImageNotFoundException:
            # print(f"Attempt {tries + 1}: Find and click failed - no Image {imagePath} found")
            tries += 1
        sleepBetween(0.2, 0.1)
    if debug:
        print(f"All attempts failed, taking a screenshot for debugging...")
        screenshotPath = takeScreenshot(region if region else [0, 0, pyautogui.size().width, pyautogui.size().height])
        print(screenshotPath)
    return False
        
def countColoredPixelsInBox(box, farbe=(223, 86, 66), anzahl=10, toleranz=10):
    x, y, breite, hoehe = box
    screenshot = pyautogui.screenshot(region=(x, y, breite, hoehe))
    color_count = 0

    # Berechne die obere und untere Grenze für jeden Farbkanal
    min_farbe = (max(0, farbe[0] - toleranz), max(0, farbe[1] - toleranz), max(0, farbe[2] - toleranz))
    max_farbe = (min(255, farbe[0] + toleranz), min(255, farbe[1] + toleranz), min(255, farbe[2] + toleranz))

    for px in range(screenshot.width):
        for py in range(screenshot.height):
            aktuelles_pixel = screenshot.getpixel((px, py))
            if all(min_farbe[i] <= aktuelles_pixel[i] <= max_farbe[i] for i in range(3)):
                color_count += 1

    print(f"Anzahl gefundener Pixel mit Farbe {farbe}: {color_count}")
    return color_count > anzahl

def most_common_colors_in_box(box, top_n=3):
    x, y, width, height = box
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    # Extrahieren aller Pixel in der Box
    pixels = [screenshot.getpixel((px, py)) for px in range(width) for py in range(height)]
    
    # Zählen der am häufigsten auftretenden Farben
    color_counts = Counter(pixels)
    most_common_colors = color_counts.most_common(top_n)
    
    # Ausgabe der Ergebnisse
    print(f"Die {top_n} häufigsten Farben und ihre Anzahlen:")
    for i in range (top_n):
        color, count = most_common_colors[i]
        # print(most_common_colors[i])
        print_color(most_common_colors[i], color)
    return most_common_colors

def print_color(text, rgb):
    # RGB-Farben verwenden den 24-bit Farbmodus
    # \033[38;2;<r>;<g>;<b>m  - Setzt die Vordergrundfarbe
    # \033[48;2;<r>;<g>;<b>m  - Setzt die Hintergrundfarbe (falls benötigt)
    color_code = f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
    reset_code = "\033[0m"
    text = str(text)
    print(color_code + text + reset_code)