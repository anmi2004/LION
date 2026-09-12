# LION add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

import addonHandler
import config
import gui
from gui import guiHelper
from gui import nvdaControls
import wx

from . import sliderMapping

addonHandler.initTranslation()


class LIONSettingsPanel(gui.settingsDialogs.SettingsPanel):
	title = _("LION")
	panelDescription = _("Modify OCR area, interval, and text similarity threshold")

	def makeSettings(self, settingsSizer: wx.BoxSizer) -> None:
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		valInterval = config.conf.getConfigValidation(("lion", "interval"))
		intervalMin = sliderMapping.intervalSecondsToSlider(float(valInterval.kwargs["min"]))
		intervalMax = sliderMapping.intervalSecondsToSlider(float(valInterval.kwargs["max"]))
		self.intervalSlider = settingsSizerHelper.addLabeledControl(
			# Translators: label for the OCR interval slider
			_("OCR &interval (seconds):"),
			nvdaControls.EnhancedInputSlider,
			minValue=intervalMin,
			maxValue=intervalMax,
		)
		self.intervalSlider.SetLineSize(1)
		self.intervalSlider.SetPageSize(10)
		self.intervalSlider.SetValue(
			sliderMapping.intervalSecondsToSlider(config.conf["lion"]["interval"])
		)

		self.targetList = settingsSizerHelper.addLabeledControl(
			# Translators: label for the OCR target choice
			_("&OCR target:"),
			wx.Choice,
			choices=[
				_("Navigator object"),
				_("Whole screen"),
				_("Current window"),
				_("Current control"),
			],
		)
		self.targetList.SetSelection(config.conf["lion"]["target"])

		valThreshold = config.conf.getConfigValidation(("lion", "threshold"))
		thresholdMin = int(float(valThreshold.kwargs["min"]) * 100)
		thresholdMax = int(float(valThreshold.kwargs["max"]) * 100)
		self.thresholdSlider = settingsSizerHelper.addLabeledControl(
			# Translators: label for the text similarity threshold slider
			_("&Text similarity threshold (%):"),
			nvdaControls.EnhancedInputSlider,
			minValue=thresholdMin,
			maxValue=thresholdMax,
		)
		self.thresholdSlider.SetLineSize(10)
		self.thresholdSlider.SetPageSize(20)
		self.thresholdSlider.SetValue(
			sliderMapping.thresholdToSlider(config.conf["lion"]["threshold"])
		)

		self.cropUpSlider = self._addCropSlider(
			settingsSizerHelper,
			_("Crop pixels from &above (%):"),
			config.conf["lion"]["cropUp"],
		)
		self.cropDownSlider = self._addCropSlider(
			settingsSizerHelper,
			_("Crop pixels from &below (%):"),
			config.conf["lion"]["cropDown"],
		)
		self.cropLeftSlider = self._addCropSlider(
			settingsSizerHelper,
			_("Crop pixels from &left (%):"),
			config.conf["lion"]["cropLeft"],
		)
		self.cropRightSlider = self._addCropSlider(
			settingsSizerHelper,
			_("Crop pixels from &right (%):"),
			config.conf["lion"]["cropRight"],
		)

		self.regexFiltersEdit = settingsSizerHelper.addLabeledControl(
			# Translators: label for the multiline regular expression filter field
			_("Regular expression filters (one per &line):"),
			wx.TextCtrl,
			style=wx.TE_MULTILINE,
			size=(-1, 100),
		)
		self.regexFiltersEdit.SetValue(config.conf["lion"].get("regexFilters", ""))
		self.regexFiltersEdit.Bind(wx.EVT_CHAR_HOOK, self.onRegexKeyHook)

	def _addCropSlider(
		self,
		helper: guiHelper.BoxSizerHelper,
		label: str,
		value: int,
	) -> nvdaControls.EnhancedInputSlider:
		slider = helper.addLabeledControl(
			label,
			nvdaControls.EnhancedInputSlider,
			minValue=0,
			maxValue=100,
		)
		slider.SetLineSize(1)
		slider.SetPageSize(10)
		slider.SetValue(value)
		return slider

	def onRegexKeyHook(self, event: wx.KeyEvent) -> None:
		"""Keep Enter inside the multiline filter instead of closing the dialog."""
		if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			self.regexFiltersEdit.WriteText("\n")
			return
		event.Skip()

	def onSave(self) -> None:
		conf = config.conf["lion"]
		conf["cropUp"] = self.cropUpSlider.GetValue()
		conf["cropLeft"] = self.cropLeftSlider.GetValue()
		conf["cropDown"] = self.cropDownSlider.GetValue()
		conf["cropRight"] = self.cropRightSlider.GetValue()
		conf["interval"] = sliderMapping.sliderToIntervalSeconds(self.intervalSlider.GetValue())
		conf["target"] = self.targetList.GetSelection()
		conf["threshold"] = sliderMapping.sliderToThreshold(self.thresholdSlider.GetValue())
		conf["regexFilters"] = self.regexFiltersEdit.GetValue()
