from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import tesserocr
import pyautogui
import cv2
import numpy as np
from locators import locateAllOnScreenWithMask
from globals import *
from ocr import *
from helpers import *
import re
import random
import cv2
import numpy as np
from PIL import Image
import tesserocr

nameZone = [1407, 400, 290, 39]
levelZone = [1247, 378, 44, 42]
classZone = [1302, 559, 215, 43]
infoZone = [1405, 502, 82, 31]
skillsZone = [1784, 501, 109, 34]
itemLevelOne = [1552, 606, 26, 23]
itemLevelTwo = [1713, 606, 26, 23]
itemLevelThree = [1879, 606, 26, 23]
itemLevelFour = [1552, 788, 26, 23]
itemLevelFive = [1713, 788, 26, 23]
itemLevelSix = [1879, 788, 26, 23]

itemQualityZone = [1087, 771, 98, 89]
itemNameZone = [1173, 580, 258, 33]
elementZone = [1241, 783, 86, 40]
spiritZone = [1382, 773, 97, 94]

qualityCommonColor = (181, 181, 181)
qualityEpicColor = (216, 112, 255)
qualityUncommonColor = (95, 255, 156)
qualityRareColor = (100, 248, 255)
qualityLegendaryColor = (255, 230, 136)

elementColorEarth = (148, 215, 74)
elementColorWater = (8, 44, 107)
elementColorDark = (26, 24, 49)
elementColorLight = (247, 231, 161)
elementColorFire = (97, 9, 24)
elementColorWind = (212, 235, 239)

def readHero():
    # get name
    name = regionToString(nameZone, color = (255, 255, 255), whitelist = "text")
    print(name)
    # if name exists in hero list, store list on pc and stop
    
    #get level
    level = regionToString(levelZone, color = (255, 255, 255), whitelist = "numbers")    
    print(level)
    
    # get class
    
    # get items
        # click item
        # get quality
        # get name
        # get element
        # get spirit
        # save
        # go to next item (until 6)
        # if 6 items, press esc
    
    # get skills
        # click skills
        # select second to left
        # store name
        # get and store next if exists
        # click info
        
    
    # go to next hero
    
    
readHero()