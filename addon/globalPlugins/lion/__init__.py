import globalPluginHandler
import addonHandler
import scriptHandler
import api
import logHandler
import gui
import tones
import vision
import textInfos
import ui
import time
import queueHandler
import threading
import config
import wx
import locationHelper
from. import lionGui
from.PPOCR_api import GetOcrApi
from difflib import SequenceMatcher
from.PIL import Image, ImageGrab
from io import BytesIO
import ctypes
import os


addonHandler.initTranslation()
active = False
prevString = ""
counter = 0
# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建PaddleOCR - json.exe的绝对路径
ocr_path = os.path.join(current_dir, "PaddleOCR", "PaddleOCR-json.exe")
# 初始化PaddleOCR - json识别器对象，传入引擎路径
ocr = GetOcrApi(ocr_path)

confspec = {
    "cropUp": "integer(0, 100, default=0)",
    "cropLeft": "integer(0, 100, default=0)",
    "cropRight": "integer(0, 100, default=0)",
    "cropDown": "integer(0, 100, default=0)",
    "target": "integer(0, 3, default=1)",
    "threshold": "float(0.0, 1.0, default=0.5)",
    "interval": "float(0.0, 10.0, default=1.0)"
}
config.conf.spec["lion"] = confspec


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Lion")
    user32 = ctypes.windll.user32
    resX, resY = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.createMenu()

    def createMenu(self):
        self.prefsMenu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
        self.lionSettingsItem = self.prefsMenu.Append(wx.ID_ANY,
                                                     # Translators: name of the option in the menu.
                                                     _("&LION Settings..."),
                                                     # Translators: tooltip text for the menu item.
                                                     _("modify OCR zone and interval"))
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.lionSettingsItem)

    def terminate(self):
        try:
            self.prefsMenu.Remove(self.lionSettingsItem)
        except wx.PyDeadObjectError:
            pass

    def onSettings(self, evt):
        from versionInfo import version_year
        status = gui.message.isModalMessageBoxActive() if version_year >= 2022 else gui.isInMessageBox
        if status:
            return
        gui.mainFrame.prePopup()
        d = lionGui.frmMain(gui.mainFrame)
        d.Show()
        gui.mainFrame.postPopup()

    def isScreenCurtainRunning(self):
        from visionEnhancementProviders.screenCurtain import ScreenCurtainProvider
        screenCurtainId = ScreenCurtainProvider.getSettings().getId()
        screenCurtainProviderInfo = vision.handler.getProviderInfo(screenCurtainId)
        return bool(vision.handler.getProviderInstance(screenCurtainProviderInfo))

    @scriptHandler.script(
        description=_("Toggle OCR"),
        gestures=["kb:NVDA+Alt+N"])
    def script_ReadLiveOcr(self, gesture):
        global active
        if self.isScreenCurtainRunning() and not active:
            ui.message(_("Please disable screen curtain before using OCR."))
            return
        tones.beep(222, 333)
        if active == False:
            active = True
            ui.message(_("lion started"))
            nav = api.getNavigatorObject()
            threading.Thread(target=self.ocrLoop).start()
        else:
            active = False
            ui.message(_("lion stopped"))

    def cropRectLTWH(self, r):
        cfg = config.conf["lion"]
        if r is None:
            return locationHelper.RectLTWH(0, 0, 0, 0)
        return locationHelper.RectLTWH(int((r.left + r.width) * cfg['cropLeft'] / 100.0),
                                      int((r.top + r.height) * cfg['cropUp'] / 100.0),
                                      int(r.width - (r.width * cfg['cropRight'] / 100.0)),
                                      int(r.height - (r.height * cfg['cropDown'] / 100.0)))

    def ocrLoop(self):
        cfg = config.conf["lion"]
        self.targets = {
            0: api.getNavigatorObject().location,
            1: self.cropRectLTWH(locationHelper.RectLTWH(0, 0, self.resX, self.resY)),
            2: self.cropRectLTWH(api.getForegroundObject().location),
            3: api.getFocusObject().location
        }
        global active
        while active == True:
            if self.isScreenCurtainRunning():
                ui.message(_("Please disable screen curtain before using Windows 10 OCR."))
            self.OcrScreen()
            time.sleep(config.conf["lion"]["interval"])

    def OcrScreen(self):
        global prevString
        global counter
        global ocr
        left, top, width, height = self.targets[config.conf["lion"]["target"]]
        try:
            # 使用PIL的ImageGrab截取屏幕
            img = ImageGrab.grab(bbox=(left, top, left + width, top + height))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            imageBytes = buffered.getvalue()
            res = ocr.runBytes(imageBytes)
            logHandler.log.info(f"OCR result: {res}")
            if res.get("code", 0)!= 100:  # 修改为判断 code 字段
                logHandler.log.warning(f"OCR engine returned non - success status: {res.get('code')}")
                return
            all_text = ""
            for line in res["data"]:
                text = line["text"]
                all_text += text + " "
            threshold = SequenceMatcher(None, prevString, all_text).ratio()
            if threshold < config.conf['lion']['threshold'] and all_text.strip():
                ui.message(all_text.strip())
                prevString = all_text.strip()
        except Exception as e:
            logHandler.log.error(f"Error in OcrScreen: {e}")

