import cv2
import numpy as np
import pyautogui


def locateAllOnScreenWithMask(search_image_path, threshold=0.97):
    # Hauptbildschirm-Screenshot machen
    # Hinweis: Hier müssen Sie die Methode anpassen, um den gesamten Bildschirm zu erfassen,
    # z.B. durch Nutzung einer Bibliothek wie mss für bessere Leistung im Vergleich zu PIL.
    screen = pyautogui.screenshot()
       # Konvertiere das PIL Image-Objekt in ein NumPy-Array
    screen_np = np.array(screen)
    
     # Konvertiere das RGB-Array (PIL default) in ein BGR-Array (OpenCV default)
    screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

    # Suchbild laden mit Transparenz (Alpha-Kanal)
    template = cv2.imread(search_image_path, cv2.IMREAD_UNCHANGED)
    hh, ww = template.shape[:2]

    # Basisbild und Alpha-Kanal extrahieren
    base = template[:, :, 0:3]
    alpha = template[:, :, 3]
    
    # cv2.imshow('Basisbild', base)
    # cv2.imshow('Maske', alpha)
    # cv2.waitKey(0)


    # Maskiertes Template-Matching durchführen
    correlation = cv2.matchTemplate(screen_bgr, base, cv2.TM_CCORR_NORMED, mask=alpha)

    # Schwellenwert anwenden, um alle Übereinstimmungen zu finden
    locations = np.where(correlation >= threshold)
    
    # if len(locations[0]) > 0:
    #     cv2.rectangle(screen_bgr, (locations[1][0], locations[0][0]), (locations[1][0] + ww, locations[0][0] + hh), (0, 255, 0), 2)
    #     cv2.imshow("Erstes Match", screen_bgr)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    
    for pt in zip(*locations[::-1]):  # Durch alle gefundenen Punkte iterieren
        yield (pt[0], pt[1], ww, hh)  # Generator, der Boxen zurückgibt