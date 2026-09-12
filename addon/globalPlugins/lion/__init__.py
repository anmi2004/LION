# LION add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

import ctypes
from difflib import SequenceMatcher
from io import BytesIO
import os
import re
import threading

import addonHandler
import api
import config
import globalPluginHandler
import gui
import locationHelper
import logHandler
import queueHandler
import screenCurtain
import scriptHandler
import tones
import ui
from PIL import ImageGrab

from .lionGui import LIONSettingsPanel
from .PPOCR_api import GetOcrApi

addonHandler.initTranslation()

_OCR_EXE_NAME = "PaddleOCR-json.exe"

_CONFSPEC = {
	"cropUp": "integer(min=0, max=100, default=0)",
	"cropLeft": "integer(min=0, max=100, default=0)",
	"cropRight": "integer(min=0, max=100, default=0)",
	"cropDown": "integer(min=0, max=100, default=0)",
	"target": "integer(min=0, max=3, default=1)",
	"threshold": "float(min=0.0, max=1.0, default=0.5)",
	"interval": "float(min=0.1, max=10.0, default=1.0)",
	"regexFilters": "string(default='')",
}


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Lion")

	def __init__(self) -> None:
		super().__init__()
		config.conf.spec["lion"] = _CONFSPEC

		self._user32 = ctypes.windll.user32
		self._user32.SetProcessDPIAware()
		self._resX = self._user32.GetSystemMetrics(0)
		self._resY = self._user32.GetSystemMetrics(1)

		self._ocr = GetOcrApi(self._getOcrPath())
		self._active = False
		self._prevString = ""
		self._stopEvent = threading.Event()
		self._ocrThread: threading.Thread | None = None

		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(LIONSettingsPanel)

	def terminate(self) -> None:
		"""Stop OCR and clean up the settings panel registration."""
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(LIONSettingsPanel)
		except ValueError:
			pass

		self._stopEvent.set()
		if self._ocrThread is not None and self._ocrThread.is_alive():
			self._ocrThread.join(timeout=1.0)
		self._ocr.exit()
		super().terminate()

	def _getOcrPath(self) -> str:
		return os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			"PaddleOCR",
			_OCR_EXE_NAME,
		)

	def _isScreenCurtainRunning(self) -> bool:
		return (
			screenCurtain.screenCurtain is not None
			and screenCurtain.screenCurtain.enabled
		)

	@scriptHandler.script(description=_("Toggle OCR"), gestures=["kb:NVDA+Alt+N"])
	def script_readLiveOcr(self, gesture) -> None:
		if self._isScreenCurtainRunning() and not self._active:
			ui.message(_("Please disable screen curtain before using OCR."))
			return

		tones.beep(222, 333)
		if not self._active:
			self._active = True
			self._stopEvent.clear()
			ui.message(_("Lion started"))
			self._ocrThread = threading.Thread(
				target=self._ocrLoop,
				name="LION-OCR",
				daemon=True,
			)
			self._ocrThread.start()
		else:
			self._active = False
			self._stopEvent.set()
			ui.message(_("Lion stopped"))

	def _getDynamicTargetRect(self) -> locationHelper.RectLTWH:
		cfg = config.conf["lion"]
		targetType = cfg["target"]
		if targetType == 0:
			obj = api.getNavigatorObject()
		elif targetType == 1:
			obj = locationHelper.RectLTWH(0, 0, self._resX, self._resY)
		elif targetType == 2:
			obj = api.getForegroundObject()
		else:
			obj = api.getFocusObject()

		baseRect = (
			obj.location
			if hasattr(obj, "location")
			else locationHelper.RectLTWH(0, 0, self._resX, self._resY)
		)
		return self._cropRectLTWH(baseRect)

	def _cropRectLTWH(self, rect: locationHelper.RectLTWH) -> locationHelper.RectLTWH:
		if not rect or rect.width <= 0 or rect.height <= 0:
			return locationHelper.RectLTWH(0, 0, self._resX, self._resY)

		cfg = config.conf["lion"]
		left = rect.left + int(rect.width * cfg["cropLeft"] / 100.0)
		top = rect.top + int(rect.height * cfg["cropUp"] / 100.0)
		width = rect.width - int(rect.width * (cfg["cropLeft"] + cfg["cropRight"]) / 100.0)
		height = rect.height - int(rect.height * (cfg["cropUp"] + cfg["cropDown"]) / 100.0)
		return locationHelper.RectLTWH(
			max(rect.left, min(left, rect.left + rect.width)),
			max(rect.top, min(top, rect.top + rect.height)),
			max(10, min(width, self._resX - left)),
			max(10, min(height, self._resY - top)),
		)

	def _ocrLoop(self) -> None:
		while not self._stopEvent.is_set():
			self._ocrScreen()
			self._stopEvent.wait(config.conf["lion"]["interval"])

	def _ocrScreen(self) -> None:
		if self._isScreenCurtainRunning():
			self._stopOcrFromWorker(
				_("Lion stopped because the screen curtain was enabled.")
			)
			return

		try:
			rect = self._getDynamicTargetRect()
			img = ImageGrab.grab(
				bbox=(rect.left, rect.top, rect.left + rect.width, rect.top + rect.height)
			)
			buffered = BytesIO()
			img.save(buffered, format="PNG")
			result = self._ocr.runBytes(buffered.getvalue())

			if result.get("code") != 100:
				return

			text = " ".join(line["text"] for line in result["data"])
			text = self._applyRegexFilters(text).strip()
			if not text:
				return

			similarity = SequenceMatcher(None, self._prevString, text).ratio()
			if similarity < config.conf["lion"]["threshold"]:
				self._prevString = text
				queueHandler.queueFunction(queueHandler.eventQueue, ui.message, text)
		except Exception as exc:
			logHandler.log.error(f"LION OCR Error: {exc}")

	def _applyRegexFilters(self, text: str) -> str:
		filters = config.conf["lion"].get("regexFilters", "").splitlines()
		for pattern in filters:
			pattern = pattern.strip()
			if not pattern:
				continue
			try:
				text = re.sub(pattern, "", text)
			except re.error:
				continue
		return text

	def _stopOcrFromWorker(self, message: str) -> None:
		self._active = False
		self._stopEvent.set()
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, message)
