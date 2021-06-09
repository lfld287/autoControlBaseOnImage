import PIL.Image
import uiautomator2 as u2
import os
import myImage.ocr as ocr
import myImage.templateMatching as tm
import time
import threading

# constatns

# 资源文件

RESOURCE_PATH = "resource/arkNights"

MISSION_NAMA = "1-7"

SCREEN_LIST = {"start": False, "login": False, "event": False,
               "supply": False, "checkin": False, "main": False}


def getCenter(pos: tuple):
    print(pos)
    left, top, right, bottom = pos
    x = left+(right-left)/2
    y = top+(bottom-top)/2
    return int(x), int(y)


class arkNights():
    def __init__(self, device: u2.Device) -> None:
        self.d = device
        self.ss = None

    def updateScreen(self):
        self.ss = self.d.screenshot()

    def checkAndStart(self):
        """
        检查当前app是不是mrfz，不是的话启动
        """
        if self.d.app_current().get("package") != "com.hypergryph.arknights":
            self.d.app_start("com.hypergryph.arknights",
                             "com.u8.sdk.U8UnityContext")

    def checkScreen(self, screen: str) -> bool:
        g = os.walk(RESOURCE_PATH+"/"+screen+"/feature")
        for root, _, files in g:
            for file in files:
                feature_img = PIL.Image.open(os.path.join(root, file))
                _, val = tm.Tmatch(self.ss, feature_img)
                if val > 0.85:
                    print(file+" match")
                    return True
        return False

    def actionClick(self, screen: str, element: str, interval: int = 2) -> bool:
        g = os.walk(RESOURCE_PATH+"/"+screen+"/action")
        result: bool
        for root, _, files in g:
            if element+".png" in files:
                element_img = PIL.Image.open(
                    os.path.join(root, element+".png"))
                pos, val = tm.Tmatch(self.ss, element_img)
                if val < 0.85:
                    print(element+" not found in screeShot")
                    result = False
                else:
                    x, y = getCenter(pos)
                    self.d.click(x, y)
                    result = True
            else:
                print(element+" not found in action folder")
                result = False
        time.sleep(interval)
        return result

    def detectCurrentScreen(self) -> str:
        for key in SCREEN_LIST:
            if SCREEN_LIST[key] == False:
                print("detect "+key)
                if self.checkScreen(key):
                    SCREEN_LIST[key] = True
                    return key
        return "unknown"

    def gotoMainMenu(self):
        while True:
            self.updateScreen()
            scr = self.detectCurrentScreen()
            if scr == "main":
                print("alredy in MainMenu")
                self.gotoTerminal()
            elif scr == "start":
                self.actionClick("start", "start_button")
            elif scr == "login":
                self.actionClick("login", "login_button")
            elif scr == "event":
                self.actionClick("event", "event_close")
            elif scr == "supply":
                self.actionClick("supply", "confirm_button")
            elif scr == "checkin":
                self.actionClick("checkin", "close_button")

    def gotoTerminal(self):
        if self.actionClick("main", "current"):
            print("alredy in Terminal")
            self.gotoFight()
        SCREEN_LIST["event"] = False
        SCREEN_LIST["main"] = False

    def gotoFight(self):
        self.updateScreen()
        if self.actionClick("fight", "exterminate"):
            print("interval exterminate")
        elif self.actionClick("fight", "main_theme"):
            print("alredy in main_theme")
            self.gotoAwaken()

    def gotoAwaken(self):
        while True:
            self.updateScreen()
            if self.actionClick("fight", "awaken"):
                print("alredy in awaken")
                self.gotoPart("evil_time_part2")

    def gotoPart(self, name: str):
        while True:
            self.updateScreen()
            if self.actionClick("fight", name):
                print("alredy in evil_time_part2")
                break
