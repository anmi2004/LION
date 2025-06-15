import os
import sys
import globalPluginHandler
import addonHandler
import scriptHandler
import api
import gui
import tones
import vision
import ui
import time
import threading
import config
import wx
import locationHelper
from . import lionGui
from .PPOCR_api import GetOcrApi
from difflib import SequenceMatcher
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageGrab
from io import BytesIO
import ctypes

addonHandler.initTranslation()

ctypes.windll.user32.SetProcessDPIAware()
user32 = ctypes.windll.user32

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Lion")

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.resX, self.resY = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.ocr = GetOcrApi(os.path.join(os.path.dirname(os.path.abspath(__file__)), "PaddleOCR", "PaddleOCR-json.exe"))
        self.active = False
        self.prevString = ""
        self.createMenu()

    def createMenu(self):
        self.prefsMenu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
        self.lionSettingsItem = self.prefsMenu.Append(
            wx.ID_ANY,
            _("&LION Settings..."),
            _("modify OCR zone and interval"))
        gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onSettings, self.lionSettingsItem)

    def terminate(self):
        try:
            self.prefsMenu.Remove(self.lionSettingsItem)
        except wx.PyDeadObjectError:
            pass
        if hasattr(self, 'ocr'):
            self.ocr.exit()

    def onSettings(self, evt):
        from versionInfo import version_year
        status = gui.message.isModalMessageBoxActive() if version_year >= 2022 else gui.isInMessageBox
        if status:
            return
        gui.mainFrame.prePopup()
        d = lionGui.MainFrame(gui.mainFrame)
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
        if self.isScreenCurtainRunning() and not self.active:
            ui.message(_("Please disable screen curtain before using OCR."))
            return
        tones.beep(222, 333)
        if not self.active:
            self.active = True
            ui.message(_("lion started"))
            threading.Thread(target=self.ocrLoop, daemon=True).start()
        else:
            self.active = False
            ui.message(_("lion stopped"))

    def getDynamicTargetRect(self):
        cfg = config.conf["lion"]
        target_type = cfg["target"]

        if target_type == 0:
            obj = api.getNavigatorObject()
        elif target_type == 1:
            obj = locationHelper.RectLTWH(0, 0, self.resX, self.resY)
        elif target_type == 2:
            obj = api.getForegroundObject()
        elif target_type == 3:
            obj = api.getFocusObject()

        base_rect = obj.location if hasattr(obj, 'location') else locationHelper.RectLTWH(0, 0, self.resX, self.resY)
        return self.cropRectLTWH(base_rect)

    def cropRectLTWH(self, r):
        if not r or r.width <= 0 or r.height <= 0:
            return locationHelper.RectLTWH(0, 0, self.resX, self.resY)

        cfg = config.conf["lion"]
        r_left, r_top = r.left, r.top
        width_full, height_full = r.width, r.height

        left = r_left + int(width_full * cfg['cropLeft'] / 100.0)
        top = r_top + int(height_full * cfg['cropUp'] / 100.0)
        width = width_full - int(width_full * (cfg['cropLeft'] + cfg['cropRight']) / 100.0)
        height = height_full - int(height_full * (cfg['cropUp'] + cfg['cropDown']) / 100.0)

        left = max(r_left, min(left, r_left + width_full))
        top = max(r_top, min(top, r_top + height_full))
        width = max(10, min(width, self.resX - left))
        height = max(10, min(height, self.resY - top))

        return locationHelper.RectLTWH(left, top, width, height)

    def ocrLoop(self):
        while self.active:
            try:
                if self.isScreenCurtainRunning():
                    ui.message(_("Please disable screen curtain before using OCR."))
                    self.active = False
                    break
                self.OcrScreen()
                time.sleep(config.conf["lion"]["interval"])
            except Exception as e:
                ui.message(_("OCR loop error, restarting..."))

    def OcrScreen(self):
        try:
            target_rect = self.getDynamicTargetRect()
            left, top, width, height = target_rect.left, target_rect.top, target_rect.width, target_rect.height

            if width <= 0 or height <= 0:
                return

            left = max(0, min(left, self.resX - 10))
            top = max(0, min(top, self.resY - 10))
            right = min(left + width, self.resX)
            bottom = min(top + height, self.resY)

            img = ImageGrab.grab(bbox=(left, top, right, bottom))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            res = self.ocr.runBytes(buffered.getvalue())

            if res.get("code", 0) != 100:
                return

            all_text = " ".join([line["text"] for line in res["data"]])
            similarity = SequenceMatcher(None, self.prevString, all_text).ratio()

            if similarity < config.conf['lion']['threshold'] and all_text.strip():
                ui.message(all_text.strip())
                self.prevString = all_text.strip()

        except Exception as e:
            if "cannot identify image file" in str(e):
                ui.message(_("Screen capture failed"))

# 配置规范
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
