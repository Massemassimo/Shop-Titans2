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


def isTradeBuy():
    pix = pyautogui.pixel(positionSellOrBuyTest[0], positionSellOrBuyTest[1])
    print(pix)
    if pix[2] == 211:
        print("Customer buys")
        return True
    elif pix[2] == 107:
        print("Customer sells")
        return False
    else:
        print("Konnte nicht erkennen, ob buy oder sell")
        return None
    
def wasSmallTalkSuccess():
    try:
        foundMatch = pyautogui.locateOnScreen("images/smallTalkSuccess.png", region=regionSmallTalkButton)
        if foundMatch is not None:
            print("Smalltalk: success")
            return True
    except pyautogui.ImageNotFoundException:
        pass

    print("Smalltalk: failure")
    return False


def takeItems():
    print("Trying to take items")
    count = 0
    while True:
        text = regionToString(regionReadyItem)
        
        print(f"Text of rightmost item:{text}")
        if ("Ready" in text):
            print("Nehmbares Item gefunden")
            #TODO: double click falls doppel-craft funktioniert nicht, muss andere methode des umgangs mit doppel-crafts suchen
            clickRegion(regionReadyItem)
            # pyautogui.sleep(0.05)
            # clickRegion(regionReadyItem)
            sleepBetween(0.5, 0.4)
            triesSpecial = 0
            while (triesSpecial < 3):
                if findAndClick("images/collectQuestRegular.png", regionFindCollectMasterpiece):
                    print("found masterpiece, pressed collect")
                    sleepBetween(0.2, 0.1)
                    break
                elif findAndClick("images/continue.png", regionFindCollectWorkerLevelUpContinue):
                    print("worker leveled up, pressed continue")
                    sleepBetween(0.2, 0.1)
                    break
                elif findAndClick("images/okGeneral.png", regionFindCollectBlueprintLevelUpOk):
                    print("blueprint leveled up, pressed ok")
                    sleepBetween(0.2, 0.1)
                    if findAndClick("images/okGeneral.png", regionFindCollectBlueprintLevelUpOk):
                        print("Took item received for leveling up blueprint")
                        # TODO: remove screen asking for item donation if item is leveled up to maximum
                    break                
                else:
                    triesSpecial += 1
        else:
            print("Keine nehmbaren Items")
            count += 1
            if count > 2:
                break
        pyautogui.sleep(1)



def sellItems():
    print(f"Verarbeite sellItems")

    erstes_match = pyautogui.locateOnScreen("images/sellItemBubble8.png", confidence=0.96)
    # exit()

    if erstes_match is None:
        print("Kein sellItemBubbles gefunden")
        return

    # Annahme: Wenn der nachfolgende Code ausgeführt wird, muss es zwingend matches gegeben haben
    # stop = False
    skipCounter = 0
    clickRegion(erstes_match)
    print("erstes sellbubble match angeklickt")
    
    while skipCounter < 5: # while not stop:
        pyautogui.sleep(0.5)
        
        # SONDERFÄLLE
        tradeStatus = isTradeBuy()
        # wenn Storykram
        if isStory():
            print("Is Storykram, skipping story")
            skipStory()
            
        elif isGiftForFriend():
            print("Gifting a friend, picking the top dude.")
            giftFirstFriend()
            
        # wenn "Restock": #TODO: Aktuell auch wenn Heldenauftrag, eigene Routine entwickeln
        elif isRestock():
            print("is Restock, clicking Refuse")
            # click refuse
            clickRegion(regionRefuseButton)
            
            sleepBetween(2, 1)
            findAndClick("images/yes.png", region=[1300, 800, 300, 200])
            continue # fang wieder von vorn an
        
        # wenn es ein kaufbares Item ist, small talk und buy        
        elif tradeStatus is False:
            print("Kaufbares Item gefunden")
            sleepBetween(2, 1)
            clickRegion(regionSmallTalkButton)
            sleepBetween(0.5, 0.2)
            clickRegion(regionSellButton)
            if skipCounter > 0:
                skipCounter = skipCounter - 1
                
        elif tradeStatus is None:
            skipCounter += 1
            continue
        else:
            print("Verkaufbares Item gefunden")
                

            
        # REGULÄRE VERKAUFSFÄLLE
                
        currentEnergy, maxEnergy = getEnergy()
        surchargeEnergy = getSurchargeEnergy()
        if surchargeEnergy == None:
            print("keine Surcharge Energy gefunden, evtl. nicht in Verkauf?")
            break
        
        # wenn es ein relativ hochpreisiges Item ist und wir genug Energie haben, surcharge, small talk, dann verkaufe
        elif surchargeEnergy > maxEnergy / 4 and surchargeEnergy <= currentEnergy:
            print("HOCHPREISIGES Item gefunden, Energie ausreichend für surcharge: BUY")
            clickRegion(regionSurchargeButton)
            sleepBetween(0.5, 0.2)
            clickRegion(regionSmallTalkButton)
            sleepBetween(0.5, 0.2)
            clickRegion(regionSellButton)
            if skipCounter > 0:
                skipCounter = skipCounter - 1
        
        # wenn es ein relativ hochpreisiges Item ist und wir NICHT genug Energie haben, skip und counter + 1, dann neuer loop
        elif surchargeEnergy > maxEnergy / 4 and surchargeEnergy > currentEnergy:
            print("HOCHPREISIGES Item gefunden, Energie NICHT AUSREICHEND für surcharge: SKIP")
            pyautogui.click(1650, 350)
            sleepBetween(0.5, 0.2)
            skipCounter = skipCounter + 1
            continue
        
        # wenn es kein hochpreisiges Item ist, smalltalk wenn currentEnergy gering, sonst skip und counter + 1, dann neuer loop
        elif surchargeEnergy <= maxEnergy / 4:
            if (currentEnergy > maxEnergy / 1.5):
                print("NICHT hochpreisig. currentEnergy HOCH: SKIP")
                pyautogui.click(1650, 350)
                sleepBetween(0.5, 0.2)
                skipCounter = skipCounter + 1
                continue
            # wenn currentEnergy gering genug, small talk
            print("NICHT hochpreisig. currentEnergy GERING: SMALL TALK")
            clickRegion(regionSmallTalkButton)
            sleepBetween(0.5, 0.2)
            # bei erfolgreichem small talk, sell item, sonst refuse tade
            if wasSmallTalkSuccess() == True:
                # wenn niedrigpreisig, discount
                if surchargeEnergy <= maxEnergy / 8:
                    print("Small talk erfolgreich und Item SEHR GÜNSTIG: DISCOUNT, dann SELL")
                    clickRegion(regionDiscountButton)
                    sleepBetween(0.5, 0.2)
                else:
                    print("Small talk erfolgreich und Item MITTELPREISIG: SELL ohne discount")
                # dann verkaufen, egal ob discounted oder nicht
                clickRegion(regionSellButton)
                sleepBetween(0.5, 0.2)
                if skipCounter > 0:
                    skipCounter = skipCounter - 1
            # small talk nicht erfolgreich
            else:
                print("Small talk NICHT erfolgreich: REFUSE")
                clickRegion(regionRefuseButton)
        else:
            print("keine Sellbedingung erfüllt, skip")
            pyautogui.click(1650, 350)
            sleepBetween(0.5, 0.2)
            skipCounter = skipCounter + 1
        
        # # sellItems finishes for some reason or another:
        # 
        # Kurze Pause nach jeder Aktion, um die UI reagieren zu lassen
        sleepBetween(1.5, 0.5)
        
    # Abschließende Actions (loop durch oder skipCounter > x)
    if findAndClick("images/waitOnSelling.png", region=regionFindWait):
        print("Stopped selling, conditions arent optimal.")
    else:
        print("wieder im Shop??")
            
 
def isStory():
    return find("images/story.png", region=regionStoryTime, confidence=0.9)

def isRestock():
    return find("images/restock.png", region=regionFindRestock, confidence=0.9)
    
def isGiftForFriend():    
    return find("images/chooseGiftReceiver.png", region=regionChooseGiftForFriend, confidence=0.9)

def giftFirstFriend():
    regionConfirmButton = [1129, 944, 302, 98]
    clickRegion(regionConfirmButton) # click confirm button
    clickRegion(regionConfirmButton) # click finish button at the same position (sleep baked into clickRegion())

def find(imagePath, region=None, confidence=0.95):
    """Versucht, das gegebene Bild zu finden. Gibt True zurück, wenn gefunden und geklickt wurde, sonst False."""
    try:
        location = pyautogui.locateOnScreen(imagePath, region=region, confidence=confidence)
        return True
    except pyautogui.ImageNotFoundException:
        return False

def skipStory():
    while True:
        # Klicken in der Mitte des Bildschirms
        pyautogui.click(1000, 500)
        # Warte eine kurze Zeitperiode
        sleepBetween(0.2, 0.1)
        
        # Prüfen, ob das Warte-Symbol gefunden werden kann
        if findAndClick("images/waitOnSelling.png", region=regionFindWait):
            # Wenn das Warte-Symbol gefunden wurde, versuchen, das Verkaufssymbol zu finden und zu klicken
            # TODO: "RESTOCK" implementieren
            if findAndClick("images/sell.png", region=regionFindSell):
                # Wenn das Verkaufssymbol gefunden und geklickt wurde, beende die Funktion
                return
            else:
                # Wenn das Verkaufssymbol nicht gefunden wurde, aber das Warte-Symbol geklickt wurde, versuche, auf waitOnSell zu klicken
                # TODO: Eventuell statt wait "refuse" als Übergang nutzen? Sonst wird ständig die "Sellbubble" des Helden gefunden und wieder geschlossen
                findAndClick("images/waitOnSelling.png", region=regionFindWait)
                return
        # Wenn das Warte-Symbol nicht gefunden wurde, wiederhole den Loop
        
    
def craftItems():
    print(f"Verarbeite craftItems")
    # lese aus, wie viele Crafting Slots offen sind
    craftingSlots = regionToString(regionCraftingSlots, threshold=200)
    
    # wenn "+" (bzw. keine Zahl lesbar), stop funktion
    try:
        # Versuche, craftingSlots in einen Integer umzuwandeln
        craftingSlots = int(craftingSlots)
        
        # Überprüfen, ob craftingSlots im erlaubten Bereich liegt
        if 1 <= craftingSlots <= 9:
            print(f"Crafting Slots: {craftingSlots}")
        else:
            print(f"craftingSlots ({craftingSlots}) ist nicht im erlaubten Bereich (1-9).")
            return
    except ValueError:
        # Wenn die Konvertierung fehlschlägt (z.B. wegen eines "+" Zeichens oder anderer nicht-numerischer Zeichen)
        print(f"craftingSlots (Output: {craftingSlots}) enthält keine lesbare Zahl.")
        return
    
    clickRegion(regionCraftingSlots)
    sleepBetween(0.2, 0.1)
    # wenn bookmark nicht gelb, clicke auf bookmark
    clickRegion(regionCraftSpecial) # klickt Sternsymbol
    sleepBetween(0.2, 0.1)
    clickRegion(regionCraftSpecial) # klickt Sternsymbol zur Sicherheit # TODO: Nötig?
    sleepBetween(0.2, 0.1)
    if findAndClick("images/capricesUnselected.png", region=regionCraftFindCaprices):
        print("caprices found and chosen")
    elif find("images/capricesSelected.png", region=regionCraftFindCaprices):
        print("caprices found, were chosen already [no action]")
    else:
        findAndClick("images/bookmarkUnselected.png", region=regionCraftFindBookmark)
        print("Bookmarked items chosen for production")
    sleepBetween(0.2, 0.1)
    # setze herzustellendesItem = 0 (ganz links)
    herzustellendesItem = 0
    #starte loop:
    while (True):
        print("sind in while schleife des crafting blocks")
        # wenn das + bei Crafting Slots zu sehen ist sind wir a) im normalen Shop Menu und b) kann kein weiteres Item gecraftet werden - Ende der Funktion
        weLeftCraftingWindow = find("images/noCraftSlotFree.png", regionCraftingSlots)
        if weLeftCraftingWindow:
            return
        
    # lese materialbedarf des herzustellendesItem aus
        region = regionsMats[herzustellendesItem]
        cannotCraft = False
        if countColoredPixelsInBox(region, farbe=(255, 102, 82)):
            cannotCraft = True
            print(f"Zu viele rote Pixel in Itemslot {herzustellendesItem + 1}")
        elif countColoredPixelsInBox(region, farbe=(72, 61, 66), anzahl = 1000):
            cannotCraft = True
            print(f"Zu viele graue Pixel in Itemslot {herzustellendesItem + 1}")
        
        if cannotCraft:            
            herzustellendesItem += 1
            if herzustellendesItem > 8:
                print("craft loop wird beendet, kein Item herstellbar")
                findAndClick("images/closeGeneral.png", [2414, 135, 132, 121])
                break # oder return?
            continue
        else:
            print(f"In Region {region} sind keine (oder wenige) rote Pixel")
            clickRegion(region)
            greenItem = countColoredPixelsInBox(regionUseItemQuality, (74, 255, 33), anzahl = 150) # grün = Superior
            whiteItem = countColoredPixelsInBox(regionUseItemQuality, (255, 255, 255), anzahl = 150) # weiss = normal
            
            if whiteItem or greenItem:
                print("Item weiß oder grün, wird verbraucht")
                print(f"Verbrauchbares Item gefunden? {findAndClick('images/yes.png', [876, 887, 798, 146])}")
            else:
                # Alternative 1: Ablehnen
                print("Item Quality zu hoch: LEHNE AB")
                findAndClick("images/no.png", regionYesNoModal)
                sleepBetween(0.2, 0.1)
                findAndClick("images/closeGeneral.png", regionCloseModal)
                herzustellendesItem += 1
                
                # ALTERNATIVE 2: Craften
                # print("Item Quality zu hoch: CRAFTE FEHLENDE COMPONENTS")
                # TODO: getComponentIcon, isolate (remove purple pixels including shadows)
                # findAndClick("images/craft.png", regionYesNoModal)
                # TODO: findAndClick isolated componentIcon (transparent)
            continue

    
def getEnergy():
    text = regionToStringWhite(regionEnergy, 200, whitelist="energy")
    
    # Entfernen aller Zeichen, die keine Ziffern, Kommata oder das Trennzeichen '/' sind
    bereinigter_text = re.sub(r"[^\d/,]", "", text)
    
    # Aufteilen des Strings am Trennzeichen und Ignorieren leerer Strings
    zahlen_strings = [zahl for zahl in bereinigter_text.split('/') if zahl]
    
    # Überprüfen der Zahlen und Anpassung basierend auf der Logik
    if len(zahlen_strings) == 2:
        currentEnergy_str, maxEnergy_str = zahlen_strings
        
        # Entferne Tausender-Trennzeichen für die Umwandlung in Integer
        currentEnergy = int(currentEnergy_str.replace(',', ''))
        maxEnergy = int(maxEnergy_str.replace(',', ''))
        
        # Logikprüfung für Tausender-Trennzeichen in der ersten Zahl
        if ',' in currentEnergy_str:
            print(f"Fehler: Tausender-Trennzeichen in einer ungültigen Position in {currentEnergy_str}. Korrigiere auf die letzten drei Ziffern.")
            currentEnergy_str = currentEnergy_str[-3:]
            currentEnergy = int(currentEnergy_str)
        
        # Überprüfen, ob CurrentEnergy größer als MaxEnergy ist
        if currentEnergy > maxEnergy:
            print(f"Fehler: CurrentEnergy ({currentEnergy}) ist größer als MaxEnergy ({maxEnergy}). Korrektur wird durchgeführt.")
            while currentEnergy > maxEnergy:
                currentEnergy_str = currentEnergy_str[1:]
                currentEnergy = int(currentEnergy_str)
        
        print(f"CurrentEnergy / maxEnergy: {currentEnergy} / {maxEnergy}")
        return [currentEnergy, maxEnergy]
    else:
        print(f"Nur eine Zahl gefunden: {zahlen_strings[0]}. Überprüfen Sie den ursprünglichen Text: {text} und bereinigten Text: {bereinigter_text}")
        return [int(zahlen_strings[0])]


    
def getSellItemPrice():
    # screenshot_region = regionDiscountEnergy
    text = regionToString(regionDiscountEnergy, whitelist="numbers")
    bereinigter_text = re.sub(r"[^\d]", "", text)
    print(f"Item Price: {bereinigter_text}")
    
    return int(bereinigter_text)
    
def getDiscountEnergy():
    # screenshot_region = regionDiscountEnergy
    text = regionToString(regionDiscountEnergy, whitelist="numbers")
    bereinigter_text = re.sub(r"[^\d]", "", text)
    print(f"Discount Energy: {bereinigter_text}")
    
    return int(bereinigter_text)

def getSurchargeEnergy():
    # try surchargable coloring (red):
    text = regionToString(regionSurchargeEnergy, color = (231, 104, 106), whitelist  ="numbers", threshold=0, callingFunction = "getSurchargeEnergy") # (231, 104, 106) = rot
    # try greyed out energy if no red text was found
    if text == "":
        print("keinen roten Text bei surcharge energy cost gefunden, probiere grau")
        text = regionToString(regionSurchargeEnergy, color = (105, 105, 105), whitelist  ="numbers", threshold=0, callingFunction = "getSurchargeEnergy") # (65, 59, 63) = grau
    # print(f"Surcharged Energy unbereinigter Text: {text}")
    bereinigter_text = re.sub(r"[^\d]", "", text)    
    print(f"Surcharge Energy: {bereinigter_text}")
    
    try:
        surchargeEnergy = int(bereinigter_text)
    except:
        print(f"Exception trying to turn '{bereinigter_text}' into an int, getSurchargeEnergy() returning none")
        return None
        
    if surchargeEnergy >= 4000:
            surchargeEnergy = surchargeEnergy - 4000 # sometimes the lighning symbol infront of the number is ocr'ed as a 4 --> bereinigter_text = 4xxx    

    
    return surchargeEnergy

def chooseNewBounty():
    # Annahme: Bounty Board ist geöffnet
    scrollCount = 0
    while (True):
        if scrollCount > 5:
            return
        if findAndClick("images/surchargeItemsBounty.png", regionBountyBoard):
            sleepBetween(1, 0.6)
            if findAndClick("images/accept.png", regionBountyBoard):
                 return
        else:
            scrollCount = scrollCount + 1
            # scroll up
            pyautogui.moveTo(pyautogui.center(regionBountyBoard))
            pyautogui.drag(0, -430, 1, button="left")
            sleepBetween(0.2, 0.1)

def claimGoals():
    if findAndClick("images/goalAchieved.png", regionFindGoals):
        findAndClick("images/claimReward.png", regionFindClaimReward)


def goToCity():
    if findAndClick("images/cityAction.png", regionFindCity):
        doStuffInCity()
        return # just so the function is not empty
        

def helpFriends():
    helpFriendsUpgrade()
    helpFriendsDustOff()

def helpFriendsDustOff():
    print("Start helping Friends dust off")
    tries = 0
    while (tries < 3):        
        if findAndClick("images/friendDust.png", regionFindFriends, 0.7):
            print("Freund gefunden, dem ich helfen kann")
            sleepBetween(1.7, 1.4)
            triesHelping = 0
            while (triesHelping < 3):
                if findAndClick("images/goToHelpAroundTheShop.png", regionFindHelpAroundTheShop):
                    triesHelping = 0
                    print("Aufgabe im Shop des Freundes gefunden")                    
                    sleepBetween(1.0, 0.8)
                    triesDusting = 0
                    while (triesDusting < 3):
                        sleepBetween(0.4, 0.2)
                        if findAndClick("images/dustOff2.png", region = [1039, 117, 526, 322]):
                            triesDusting = 0
                            print("Dusting off")
                            sleepBetween(4.0, 0.3)
                        else:
                            print("No dust off job found")
                            triesDusting = triesDusting + 1
                    print("Dustoff erledigt")                    
                else:
                    sleepBetween(0.4, 0.2)
                    print("Keine Aufgaben im Shop des Freundes gefunden")
                    triesHelping = triesHelping + 1
                    
                    triesClaiming = 0
                    while (triesClaiming < 3):
                        sleepBetween(0.4, 0.2)
                        if findAndClick("images/claimReward2.png", region = [1055, 137, 452, 129]):
                            triesClaiming = 0
                            print("Claiming Reward")
                            sleepBetween(2.0, 1.3)
                            pyautogui.click(1281, 1310) # "Continue"
                            sleepBetween(2.0, 1.3)
                            # pyautogui.press("esc")
                        else:
                            print("No claim reward option found")
                            triesClaiming = triesClaiming + 1
                    
                    # TODO: click OK oder so für Annahme des Friendship-Level-Anstiegs
                    if find("images/friendshipIncreased.png", [954, 343, 675, 186], 0.7):
                        pyautogui.click(1060, 1310) # "OK"
                        sleepBetween(0.3, 0.2)
                    # TODO: Evtl.Close?
                    findAndClick("images/closeGeneral.png", [2410, 37, 146, 150], 0.7)
                    continue
        else:
            tries = tries + 1
            sleepBetween(0.3, 0.1)
            print("Keine Freunde gefunden, die Hilfe mit dem Abstauben brauchen")
            continue


def helpFriendsUpgrade():
    print("Start helping Friends upgrade")
    if findAndClick("images/friendHelpUpgrades3.png", region = regionFindFriends, grayscale = True, confidence=0.7):
        print("Freunde brauchen Hilfe mit Upgrades")
        sleepBetween(0.4, 0.2)
        pyautogui.click(1292, 1009) # "Help all"
        sleepBetween(0.2, 0.1)
        findAndClick("images/closeGeneral.png", [1549, 383, 146, 128], confidence=0.7)
    else:
        print("No friends needing help upgrading found")
        return

def quest():
    print("Questing")
    finishQuests()
    startQuests()
    
    
def finishQuests():
    count = 0
    while count < 3:
        text = regionToString(regionFindReadyQuest)
        
        print(f"Quest Ready? Text:{text}")
        if ("Ready" in text):
            print("Quest Ready")
            #double click falls doppel-craft
            clickRegion(regionFindReadyQuest)
            sleepBetween(0.2, 0.1)
            clickRegion(regionFindReadyQuest)
            triesCollectRewards = 0
            while triesCollectRewards < 5:
                sleepBetween(2.8, 2.5)
                if findAndClick("images/collectQuestPremium.png", regionFindCollectAll):
                    break
                else:
                    print("Waiting, Kein 'Collect Premium' gefunden")
                    # Repair items falls nötig
                    regionRepairItems = [1103, 448, 349, 116]
                    if find("images/repairItems.png", regionRepairItems, 0.8):
                        print("Repair items gefunden")
                        regionShowAll = [1305, 914, 294, 86]
                        clickRegion(regionShowAll)
                        sleepBetween(0.2, 0.1)
                        regionRepairWithGold = [1659, 713, 383, 74]
                        findAndClick("images/repairWithGold.png", regionRepairWithGold, 0.8)
                        sleepBetween(0.2, 0.1)
                        triesCollectRewards = 0
                                                    
                    triesCollectRewards += 1
                    continue
        else:
            print("No Quest Ready")
            count = count + 1
        pyautogui.sleep(1)


def startQuests():
    print("starting Quests")
    
def trade():
    print("Trading")
    openMarket()
    closeSoldListings()
    listNewItems() # only mats for starters?
    buyGoodOffers()
    # TODO: Return to city screen

def openMarket():
    print("Opening Markets")
    # findAndClick("images/goToShop.png", regionFindCity, confidence= 0.7)

def closeSoldListings():
    print("Closing sold listings")

def listNewItems():
    print("Listing new Items (mats)")

def buyGoodOffers():
    print("Buying good offers")

    
def goToShop():
    print("Going to shop")
    findAndClick("images/goToShop.png", regionFindCity, confidence= 0.7)
    doStuffInShop()


def doStuffInShop():
    print("Doing stuff in Shop")
    takeItems()
    craftItems()
    sellItems()
    # claimGoals()
    # ChooseNewBounty()
    goToCity()
    

def doStuffInCity():
    print("Doing stuff in City")
    quest()
    helpFriends()
    trade()
    goToShop()
    
    


# for i in range(1):
#     print(getEnergy())

# countColoredPixelsInBox(regionSurchargeEnergy, (97, 96, 97)) # grau:  (65, 59, 63), rot: (231, 104, 106), anderes grau: (97, 96, 97)
# print(getSurchargeEnergy())

# textRot = regionToString(regionSurchargeEnergy, color = (231, 104, 106), whitelist  ="numbers", threshold=0, callingFunction = "getSurchargeEnergy")
# textGrau = regionToString(regionSurchargeEnergy, color = (65, 59, 63), whitelist  ="numbers", threshold=0, callingFunction = "getSurchargeEnergy")
# textGrau = regionToString(regionSurchargeEnergy, color = (97, 96, 97), whitelist  ="numbers", threshold=0, callingFunction = "getSurchargeEnergy")
# textGrau = regionToString(regionSurchargeEnergy, color = (105, 105, 105), whitelist  ="numbers", threshold=0, callingFunction = "getSurchargeEnergy") 
# print(textRot)

# print(regionToString([1882, 50, 130, 44], (255, 255, 255), 0))
# print(getEnergy())
# helpFriendsUpgrade()
# helpFriendsDustOff()

# doStuffInShop()
# doStuffInCity()

def energyPatternMatching(text):
    pattern = r'(\d{1,4}(?:,\d{3})?)/(\d{1},\d{3})'
    return re.match(pattern, text) is not None

def extractEnergyFromMatchingPattern(text):
    pattern = r'(\d{1,4}(?:,\d{3})?)/(\d{1},\d{3})'
    match = re.match(pattern, text)
    currentEnergy_str, maxEnergy_str = match.groups()
    currentEnergy = int(currentEnergy_str.replace(',', ''))
    maxEnergy = int(maxEnergy_str.replace(',', ''))
    
    print(f"CurrentEnergy / maxEnergy: {currentEnergy} / {maxEnergy}")
    return [currentEnergy, maxEnergy]
    
    
def getEnergy2(text):
    # text = regionToStringWhite(regionEnergy, 200, whitelist="energy")
    
    if energyPatternMatching(text):
            return extractEnergyFromMatchingPattern(text)
        
    # Versuch, den Fehler im Text zu korrigieren
    pattern_b = r'1(\d{1},\d{3})'
    fixed_part = re.sub(pattern_b, r'/\1', text[-6:])
    
    # Neuen Text zusammenfügen
    new_text = text[:-6] + fixed_part
    
    if energyPatternMatching(new_text):
        return extractEnergyFromMatchingPattern(new_text)
    else:
        print(f"Fehler: Text passt nicht zum erwarteten Muster. Text: {text}")
        print(f"Versuchter neuer Text: {new_text}")
        return [0, 0]

    # PATTERN FIXING ATTEMPTS
    # 1. prüfen ob letzte 6 Zeichen des Textes (string_b) das pattern "/x,xxx" (pattern_b) haben
    # 2. falls letzte 6 Zeichen das falsche pattern haben: prüfen, ob dort, wo "/" erwartet wird "1" steht (ob sie das pattern haben "1x,xxx")
    # 3. falls dort statt / eine 1 steht: diese 1 mit / ersetzen und neuen string_b mit pattern_b matchen.
    # 4. falls string_b mit pattern_b matcht, string_a und neuen string_b zusammenfügen und gesamtstring erneut pattern-matchen (energyPatternMatching(text))
    # 5. falls returnwert von energyPatternMatching(neuer_gesamtstring) True, return extractEnergyOfMatchingPattern(text)
    # 6. falls string_b mit pattern_b in 4. nicht matchte, print Fehlermeldung mit Ausgabe des string_b zu debugging-zwecken. Dann funktion beenden
    # 7. falls string_b mit pattern_b in 4. matchte aber der Gesamtstring bei 5. nicht matchte, muss in string_a (text abzüglich string_b) der fehler sein:
    # 8. print Fehlermeldung mit Ausgabe des string_a zu debugging-zwecken. Dann funktion beenden
        

# text = "1,111/2,111"
# text = "3/1,234"
# text = "1,11112,111"
text = "1,1/1/2,111"

getEnergy2(text)

# corrected_text = re.sub(r'(\d)1(\d)', r'\1/\2', text)  # Ersetzt '1' durch '/', wenn zwischen Zahlen
# bereinigter_text = re.sub(r"[^\d/,]", "", corrected_text)  # Bereinigt den Text
# corrected_text = re.sub(r'(\d)1(\d)', r'\1/\2', text)
# print(f"Text {text} wird dann zu {corrected_text} und bereinigt zu {bereinigter_text}")

# finishQuests()

# print(countColoredPixelsInBox(regionUseItemQuality, farbe = colorQualityGreen, anzahl = 30))
# print(countColoredPixelsInBox(regionUseItemQuality, farbe = colorQualityWhite, anzahl = 30))
# print(countColoredPixelsInBox(regionUseItemQuality, farbe = colorQualityBlue, anzahl = 30))

# takeAndShowScreenshot(regionYesNoModal)