import pyautogui
import keyboard
import time
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageGrab
from helpers import *

def capture_rectangle_by_key():
    points = []

    print("Drücke 'f' um Punkte zu markieren, 'p' um RGB Pixelwert an Mousecursor auszulesen, 'h' für mouse position und rgb pixelwert, 'ESC' zum Abbrechen.")
    while True:
        try:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:  # Prüfen, ob die Taste gedrückt wurde
                if event.name == 'f':
                    pos = pyautogui.position()
                    points.append(pos)
                    # print(f"Punkt gespeichert: {pos}")
                    
                    if len(points) == 2:
                        x1, y1 = points[0]
                        x2, y2 = points[1]
                        x = min(x1, x2)
                        y = min(y1, y2)
                        breite = abs(x2 - x1)
                        hoehe = abs(y2 - y1)
                        rectangle = [x, y, breite, hoehe]
                        print(f"Rechteck: {rectangle}")
                        points = []  # Punkteliste zurücksetzen für das nächste Rechteck

                elif event.name == 'p':
                    pos = pyautogui.position()
                    screenshot = ImageGrab.grab(bbox=(pos[0], pos[1], pos[0]+1, pos[1]+1))
                    rgb = screenshot.getpixel((0, 0))
                    (f"RGB Wert an Cursor: {rgb}")
                
                elif event.name == 'h':
                    pos = pyautogui.position()
                    screenshot = ImageGrab.grab(bbox=(pos[0], pos[1], pos[0]+1, pos[1]+1))
                    print(f"x: {pos[0]}, y: {pos[1]}, RGB: {screenshot.getpixel((0, 0))}")
                    
                elif event.name == "c":
                    pos = pyautogui.position()
                    points.append(pos)
                    if len(points) == 2:
                        x1, y1 = points[0]
                        x2, y2 = points[1]
                        x = min(x1, x2)
                        y = min(y1, y2)
                        breite = abs(x2 - x1)
                        hoehe = abs(y2 - y1)
                        rectangle = [x, y, breite, hoehe]
                        
                        most_common_colors_in_box(rectangle, top_n=3)
                        points = []  # Punkteliste zurücksetzen für das nächste Rechteckcc
                    
                elif event.name == 'esc':
                    print("Abbruch durch Benutzer.")
                    break

        except RuntimeError as e:  # Fängt Exceptions von keyboard.read_event
            print(f"RuntimeError: {str(e)}")
            continue

capture_rectangle_by_key()