import ctypes
import os
import threading
import time
from difflib import SequenceMatcher
from io import BytesIO

import addonHandler
import api
import config
import globalPluginHandler
import gui
import locationHelper
import logHandler
import scriptHandler
import tones
import ui
import vision
from PIL import ImageGrab

from .lionGui import LIONSettingsPanel
from .PPOCR_api import GetOcrApi


addonHandler.initTranslation()

active = False
prevString = ""
counter = 0

ctypes.windll.user32.SetProcessDPIAware()  # 声明DPI感知
user32 = ctypes.windll.user32
resX, resY = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

current_dir = os.path.dirname(os.path.abspath(__file__))
ocr_path = os.path.join(current_dir, "PaddleOCR", "PaddleOCR-json.exe")
ocr = GetOcrApi(ocr_path)

confspec = {
	"cropUp": "integer(min=0, max=100, default=0)",
	"cropLeft": "integer(min=0, max=100, default=0)",
	"cropRight": "integer(min=0, max=100, default=0)",
	"cropDown": "integer(min=0, max=100, default=0)",
	"target": "integer(min=0, max=3, default=1)",
	"threshold": "float(min=0.0, max=1.0, default=0.5)",
	"interval": "float(min=0.0, max=10.0, default=1.0)",
}
config.conf.spec["lion"] = confspec


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Lion")

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(LIONSettingsPanel)

	def terminate(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(LIONSettingsPanel)
		ocr.exit()

	def isScreenCurtainRunning(self):
		from visionEnhancementProviders.screenCurtain import ScreenCurtainProvider

		screenCurtainId = ScreenCurtainProvider.getSettings().getId()
		screenCurtainProviderInfo = vision.handler.getProviderInfo(screenCurtainId)
		return bool(vision.handler.getProviderInstance(screenCurtainProviderInfo))

	@scriptHandler.script(description=_("Toggle OCR"), gestures=["kb:NVDA+Alt+N"])
	def script_ReadLiveOcr(self, gesture):
		global active
		if self.isScreenCurtainRunning() and not active:
			ui.message(_("Please disable screen curtain before using OCR."))
			return
		tones.beep(222, 333)
		if not active:
			active = True
			ui.message(_("lion started"))
			threading.Thread(target=self.ocrLoop).start()
		else:
			active = False
			ui.message(_("lion stopped"))

	def getDynamicTargetRect(self):
		"""实时获取目标区域"""
		cfg = config.conf["lion"]
		target_type = cfg["target"]

		if target_type == 0:
			obj = api.getNavigatorObject()
		elif target_type == 1:
			obj = locationHelper.RectLTWH(0, 0, resX, resY)
		elif target_type == 2:
			obj = api.getForegroundObject()
		elif target_type == 3:
			obj = api.getFocusObject()

		base_rect = obj.location if hasattr(obj, "location") else locationHelper.RectLTWH(0, 0, resX, resY)
		return self.cropRectLTWH(base_rect)

	def cropRectLTWH(self, r: locationHelper.RectLTWH):
		"""修正后的裁剪区域计算"""
		if not r or r.width <= 0 or r.height <= 0:
			return locationHelper.RectLTWH(0, 0, resX, resY)

		cfg = config.conf["lion"]
		left = r.left + int(r.width * cfg["cropLeft"] / 100.0)
		top = r.top + int(r.height * cfg["cropUp"] / 100.0)
		width = r.width - int(r.width * (cfg["cropLeft"] + cfg["cropRight"]) / 100.0)
		height = r.height - int(r.height * (cfg["cropUp"] + cfg["cropDown"]) / 100.0)

		# 边界保护
		left = max(r.left, min(left, r.left + r.width))
		top = max(r.top, min(top, r.top + r.height))
		width = max(10, min(width, resX - left))
		height = max(10, min(height, resY - top))

		return locationHelper.RectLTWH(left, top, width, height)

	def ocrLoop(self):
		global active
		while active:
			if self.isScreenCurtainRunning():
				ui.message(_("Please disable screen curtain before using OCR."))
			self.OcrScreen()
			time.sleep(config.conf["lion"]["interval"])

	def OcrScreen(self):
		global prevString, ocr
		try:
			# 实时获取目标区域
			target_rect = self.getDynamicTargetRect()
			left, top, width, height = (
				target_rect.left,
				target_rect.top,
				target_rect.width,
				target_rect.height,
			)

			# 截图区域验证
			if width <= 0 or height <= 0:
				logHandler.log.warning(f"Invalid capture area: {target_rect}")
				return

			# 边界保护
			left = max(0, min(left, resX - 10))
			top = max(0, min(top, resY - 10))
			right = min(left + width, resX)
			bottom = min(top + height, resY)

			img = ImageGrab.grab(bbox=(left, top, right, bottom))
			buffered = BytesIO()
			img.save(buffered, format="PNG")
			res = ocr.runBytes(buffered.getvalue())

			if res.get("code", 0) != 100:
				# logHandler.log.warning(f"OCR error: {res.get('code')}")
				return

			all_text = " ".join([line["text"] for line in res["data"]])
			similarity = SequenceMatcher(None, prevString, all_text).ratio()

			if similarity < config.conf["lion"]["threshold"] and all_text.strip():
				ui.message(all_text.strip())
				prevString = all_text.strip()

		except Exception as e:
			logHandler.log.error(f"OCR Error: {str(e)}")
			if "cannot identify image file" in str(e):
				ui.message(_("Screen capture failed"))
