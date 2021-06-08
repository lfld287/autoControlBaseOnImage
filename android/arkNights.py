import PIL.Image
import uiautomator2 as u2
import os
import myImage.ocr as ocr
import myImage.templateMatching as tm
import time

# constatns

# 资源文件

RESOURCE_PATH = "resource/arkNights"

SCREEN_LIST = ["start", "login", "event", "supply", "checkin", "main"]


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
                if val < 0.85:
                    print(file+" mismatch")
                    return False
        return True

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
        for scr in SCREEN_LIST:
            if self.checkScreen(scr):
                return scr
        return "unknown"

    def gotoMainMenu(self):
        self.updateScreen()
        while True:
            scr = self.detectCurrentScreen()
            if scr == "main":
                break
            elif scr == "start":
                self.actionClick("start", "start_button")
            elif scr == "login":
                self.actionClick("login", "login_button")
            elif scr == "event":
                self.actionClick("event", "close_button")
            elif scr == "supply":
                self.actionClick("supply", "confirm_button")
            elif scr == "checkin":
                self.actionClick("checkin", "close_button")
            else:
                print("scr unknown")
            self.updateScreen()
        print("alredy in main screen")
        return

    def MainToWarehouse(self):
        self.gotoMainMenu()
        self.actionClick("main","warehouse")

    


def goToMainMenu(d: u2.Device) -> bool:
    img = d.screenshot()
    if checkIsStartScreen(d, img):
        checkAndPassStartScreen(d)
    return False


def checkIsStartScreen(d: u2.Device, img: PIL.Image.Image) -> bool:
    temp = PIL.Image.open(RESOURCE_PATH+"/start_menu_start.png")
    _, val = tm.Tmatch(img, temp)
    if val < 0.85:
        print("is not like start screen")
        return False
    else:
        print("is like start screen")
        return True


def checkAndPassStartScreen(d: u2.Device) -> bool:
    img = d.screenshot()
    temp = PIL.Image.open(RESOURCE_PATH+"/start_menu_start.png")
    pos, val = tm.Tmatch(img, temp)
    print(pos, val)
    if val < 0.85:
        return False
    print("found start,clicking")
    x, y = getCenter(pos)
    print(x)
    print(y)
    d.click(x, y)
    return True


def testList(d: u2.Device):
    img = d.screenshot()
    list = ocr.ListWord(img)
    for i in list:
        print(type(i))
        print(i)
        print(type(i[0]))
        print(i[1])
    img.show()
