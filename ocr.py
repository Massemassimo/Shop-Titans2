from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import tesserocr
import pyautogui
import cv2
import numpy as np
from locators import locateAllOnScreenWithMask
from globals import *
import re
import random
import cv2
import numpy as np
from PIL import Image
import tesserocr
from helpers import *

whitelists = {
    "default": "",  # Standardmäßig alle Zeichen zulassen
    "energy": "0123456789,/",
    "numbers": "0123456789",
    "text": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
}


def outlinedTextToString(image, threshold = 100, whitelist="default", callingFunction=""):
    
    # Abbruch, wenn das übergebene Bild kein PIL Image-Objekt ist
    if not isinstance(image, Image.Image):
        print("Das übergebene Objekt ist kein PIL Image-Objekt.")
        return None
    
    # Das Bild ist ein PIL Image-Objekt, fahre mit der Verarbeitung fort
    
    # Konvertiere das PIL Image-Objekt in ein NumPy-Array
    image_np = np.array(image)
    
     # Konvertiere das RGB-Array (PIL default) in ein BGR-Array (OpenCV default)
    image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    # Konvertierung nach Graustufen
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # Gaussian Blur.. sinnvoll?
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # Anwendung eines binären Schwellenwerts (INV --> gefundene Werte sind weiß auf schwarz)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # _, binary = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)

    # Vorbereitung für floodFill
    # Erstellen eines leeren Bildes, das 2 Pixel größer ist als das Originalbild
    h, w = binary.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)

    # FloodFill von außen mit Schwarz
    # Hier gehen wir durch jeden äußersten Pixel und wenden floodFill an
    for row in range(h):
        cv2.floodFill(binary, mask, (0, row), 0)
        cv2.floodFill(binary, mask, (w-1, row), 0)
    for col in range(w):
        cv2.floodFill(binary, mask, (col, 0), 0)
        cv2.floodFill(binary, mask, (col, h-1), 0)

    # Farben umkehren
    final_image = cv2.bitwise_not(binary)
    
    # Stacking images 
    # blurred_3_channel = cv2.cvtColor(blurred, cv2.COLOR_GRAY2BGR)
    # binary_3_channel = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    # final_image_3_channel = cv2.cvtColor(final_image, cv2.COLOR_GRAY2BGR)
    
    # height, width, _ = image_bgr.shape
    
    # if height > width:
    #     stackedImage = np.hstack((image_bgr, blurred_3_channel, binary_3_channel, final_image_3_channel))
    # else:
    #     stackedImage = np.hstack((image_bgr, blurred_3_channel, binary_3_channel, final_image_3_channel))
    # cv2.imshow('Numpy Stacked', stackedImage)
    
    # cv2.imshow('Floodfilled Image', final_image)
    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    final_pil_image = Image.fromarray(final_image)
    
    if whitelist in whitelists:
        whitelist = whitelists[whitelist]
    
        # Erstellen des API-Objekts und Einstellen der OCR-Engine mit PSM SINGLE_LINE
    with tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_LINE) as api:
        # Setze die Whitelist für erlaubte Zeichen, wenn nicht leer
        if whitelist:
            api.SetVariable("tessedit_char_whitelist", whitelist)

        # Bild für die OCR setzen
        api.SetImage(final_pil_image)

        # OCR ausführen
        text = api.GetUTF8Text().strip()

    print(f"Returned Text from outlinedTextToString: {text}.")
    print(f"Whitelist: {whitelist}. Calling Function: {callingFunction}")
    return text

def whiteTextToString(image, threshold=200, whitelist="default", callingFunction=""):
    return coloredTextToString(image, (255, 255, 255), threshold, whitelist, callingFunction)

def regionToString(screenshot_region, color=(255, 255, 255), threshold = 100, whitelist = "default", callingFunction=""):
    screenshot = pyautogui.screenshot(region=screenshot_region)
    # return outlinedTextToString(screenshot, threshold, callingFunction=callingFunction)
    return coloredTextToString(screenshot, color, threshold, whitelist, callingFunction)

def regionToStringWhite(screenshot_region, threshold = 100, whitelist = "default", callingFunction=""):
    screenshot = pyautogui.screenshot(region=screenshot_region)
    return whiteTextToString(screenshot, threshold, whitelist, callingFunction)


# test overwriting the existing function
def coloredTextToString(image, color=(231, 104, 106), threshold = 0, whitelist="default", callingFunction=""):
    if not isinstance(image, Image.Image):
        print("Das übergebene Objekt ist kein PIL Image-Objekt.")
        return None

    # Konvertiere das PIL Image-Objekt direkt in ein NumPy-Array
    image_np = np.array(image)

    # Isoliere die spezifische RGB-Farbe
    exact_color = np.array(color)
    # print(f"Threshold: {threshold}")
    lower = np.maximum(exact_color - threshold, 0)  # Keine negativen Werte
    upper = np.minimum(exact_color + threshold, 255)  # Keine Werte über 255
    mask = cv2.inRange(image_np, lower, upper)

    # Überprüfen, ob überhaupt Pixel gefunden wurden
    if np.any(mask):
        print("Pixel mit der exakten Farbe gefunden.")
    else:
        print("Keine Pixel mit der exakten Farbe gefunden.")

    result = cv2.bitwise_and(image_np, image_np, mask=mask)

    # Umwandeln in ein binäres Bild für die OCR
    gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    # Invertieren des Bildes
    final_image = cv2.bitwise_not(binary)

    # Zurückwandeln in ein PIL-Image für tesserocr
    final_pil_image = Image.fromarray(final_image)
    
    # # Preparing Images for stacking
    # image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    # mask = cv2.cvtColor(mask, cv2.COLOR_RGB2BGR)
    # gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    # binary = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    # final_image = cv2.cvtColor(final_image, cv2.COLOR_GRAY2BGR)
    
    # # Stacking images
    # height, width, _ = image_bgr.shape
    
    # if height > width:
    #     stackedImage = np.hstack((image_bgr, mask, result, gray, binary, final_image))
    # else:
    #     stackedImage = np.hstack((image_bgr, mask, result, gray, binary, final_image))
    # cv2.imshow('Numpy Stacked', stackedImage)    
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    if whitelist in whitelists:
        whitelist = whitelists[whitelist]    

    with tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_LINE) as api:
        if whitelist:
            api.SetVariable("tessedit_char_whitelist", whitelist)
            print(whitelist)
        else:
            print("Keine Whitelist")
        api.SetImage(final_pil_image)
        text = api.GetUTF8Text().strip()

    print(f"Returned Text from coloredTextToString: {text}")
    print(f"Whitelist: {whitelist}. Calling Function: {callingFunction}")
    return text


# def whiteTextToString(image, threshold=200, whitelist="default", callingFunction=""):
#     if not isinstance(image, Image.Image):
#         print("Das übergebene Objekt ist kein PIL Image-Objekt.")
#         return None

#     # Konvertiere das PIL Image-Objekt in ein NumPy-Array und dann in ein BGR-Array
#     image_np = np.array(image)
#     image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

#     # Konvertierung nach Graustufen und Isolierung der weißen Pixel
#     gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
#     _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

#     # Invertieren des Bildes, um weiße Texte zu erfassen
#     final_image = cv2.bitwise_not(binary)
    
#     # cv2.imshow('black and white Image', final_image)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()

#     # Erstellen des API-Objekts und Einstellen der OCR-Engine mit PSM SINGLE_LINE


#     if whitelist in whitelists:
#         whitelist = whitelists[whitelist]

#     with tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_LINE) as api:
#         if whitelist:
#             api.SetVariable("tessedit_char_whitelist", whitelist)
#         api.SetImage(Image.fromarray(final_image))
#         text = api.GetUTF8Text().strip()

#     print(f"Returned Text from outlinedTextToString: {text}.")
#     print(f"Whitelist: {whitelist}. Calling Function: {callingFunction}")
#     return text

# def coloredTextToString(image, color=(255, 255, 255), threshold=200, whitelist="default", callingFunction=""):
#     if not isinstance(image, Image.Image):
#         print("Das übergebene Objekt ist kein PIL Image-Objekt.")
#         return None

#     # Konvertiere das PIL Image-Objekt in ein NumPy-Array und dann in ein BGR-Array
#     image_np = np.array(image)
#     image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    
#     # Isoliere die spezifische Farbe
#     lower = np.array([max(0, c - threshold) for c in color])
#     upper = np.array([min(255, c + threshold) for c in color])
#     mask = cv2.inRange(image_bgr, lower, upper)
#     result = cv2.bitwise_and(image_bgr, image_bgr, mask=mask)
    
#     print("Lower threshold:", lower)
#     print("Upper threshold:", upper)

#     # Konvertiere das Ergebnis in Graustufen und dann in ein binäres Bild
#     gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
#     _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

#     # Invertieren des Bildes, falls der Text heller als der Hintergrund ist
#     final_image = cv2.bitwise_not(binary)
    
#     # Preparing Images for stacking
#     gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
#     binary = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
#     final_image = cv2.cvtColor(final_image, cv2.COLOR_GRAY2BGR)
    
#     # Stacking images
#     height, width, _ = image_bgr.shape
    
#     if height > width:
#         stackedImage = np.hstack((image_bgr, result, gray, binary, final_image))
#     else:
#         stackedImage = np.hstack((image_bgr, result, gray, binary, final_image))
#     cv2.imshow('Numpy Stacked', stackedImage)    
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

#     # Erstellen des API-Objekts und Einstellen der OCR-Engine mit PSM SINGLE_LINE
#     # whitelists = {
#     #     "default": "",  # Standardmäßig alle Zeichen zulassen
#     #     "energy": "0123456789,/",
#     #     "numbers": "0123456789"
#     # }

#     if whitelist in whitelists:
#         whitelist = whitelists[whitelist]

#     with tesserocr.PyTessBaseAPI(psm=tesserocr.PSM.SINGLE_LINE) as api:
#         if whitelist:
#             api.SetVariable("tessedit_char_whitelist", whitelist)
#         api.SetImage(Image.fromarray(final_image))
#         text = api.GetUTF8Text().strip()

#     print(f"Returned Text from coloredTextToString: {text}.")
#     print(f"Whitelist: {whitelist}. Calling Function: {callingFunction}")
#     return text