# LION add-on for NVDA
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2025 hwf1324 <1398969445@qq.com>

import addonHandler
import config
import gui
from gui import guiHelper
from gui import nvdaControls

import wx


addonHandler.initTranslation()


class LIONSettingsPanel(gui.settingsDialogs.SettingsPanel):
	title = _("LION")

	panelDescription = _("modify OCR zone and interval")

	def makeSettings(self, settingsSizer: wx.BoxSizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

		intervalMin = int(float(config.conf.getConfigValidation(("lion", "interval")).kwargs["min"]) * 100)
		intervalMax = int(float(config.conf.getConfigValidation(("lion", "interval")).kwargs["max"]) * 100)
		intervalLabelText = _("OCR &interval (ms):")
		self.intervalEdit = settingsSizerHelper.addLabeledControl(
			intervalLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=intervalMin,
			max=intervalMax,
			initial=int(config.conf["lion"]["interval"] * 100),
		)

		targetListLabelText = _("&OCR target:")
		self.targetList = settingsSizerHelper.addLabeledControl(
			targetListLabelText,
			wx.Choice,
			choices=[
				_("Navigator object"),
				_("Whole Screen"),
				_("current window"),
				_("current control"),
			],
		)
		self.targetList.SetSelection(config.conf["lion"]["target"])

		similarityThresholdMin = int(float(config.conf.getConfigValidation(("lion", "threshold")).kwargs["min"]) * 100)
		similarityThresholdMax = int(float(config.conf.getConfigValidation(("lion", "threshold")).kwargs["max"]) * 100)
		similarityThresholdLabelText = _("&Text similarity threshold (%):")
		self.similarityThresholdEdit = settingsSizerHelper.addLabeledControl(
			similarityThresholdLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=similarityThresholdMin,
			max=similarityThresholdMax,
			initial=config.conf["lion"]["threshold"],
		)

		cropUpLabelText = _("Crop pixels from &above (%):")
		self.cropUpEdit = settingsSizerHelper.addLabeledControl(
			cropUpLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=0,
			max=100,
			initial=config.conf["lion"]["cropUp"],
		)

		cropDownLabelText = _("crop pixels from &below(%):")
		self.cropDownEdit = settingsSizerHelper.addLabeledControl(
			cropDownLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=0,
			max=100,
			initial=config.conf["lion"]["cropDown"],
		)

		cropLeftLabelText = _("crop pixels from &left(%):")
		self.cropLeftEdit = settingsSizerHelper.addLabeledControl(
			cropLeftLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=0,
			max=100,
			initial=config.conf["lion"]["cropLeft"],
		)

		cropRightLabelText = _("crop pixels from &right (%):")
		self.cropRightEdit = settingsSizerHelper.addLabeledControl(
			cropRightLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=0,
			max=100,
			initial=config.conf["lion"]["cropRight"],
		)

	def onSave(self):
		config.conf["lion"]["cropUp"] = self.cropUpEdit.GetValue()
		config.conf["lion"]["cropLeft"] = self.cropLeftEdit.GetValue()
		config.conf["lion"]["cropDown"] = self.cropDownEdit.GetValue()
		config.conf["lion"]["cropRight"] = self.cropRightEdit.GetValue()
		config.conf["lion"]["interval"] = float(self.intervalEdit.GetValue() / 100)
		config.conf["lion"]["target"] = self.targetList.GetSelection()
		config.conf["lion"]["threshold"] = float(self.similarityThresholdEdit.GetValue() / 100)
