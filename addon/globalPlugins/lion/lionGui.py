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

		intervalMin = float(config.conf.getConfigValidation(("lion", "interval")).kwargs["min"])
		intervalMax = float(config.conf.getConfigValidation(("lion", "interval")).kwargs["max"])
		intervalLabelText = _("OCR &interval:")
		self.intervalEdit = settingsSizerHelper.addLabeledControl(
			intervalLabelText,
			wx.SpinCtrlDouble,
			min=intervalMin,
			max=intervalMax,
			initial=config.conf["lion"]["interval"],
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

		similarityThresholdMin = float(config.conf.getConfigValidation(("lion", "threshold")).kwargs["min"])
		similarityThresholdMax = float(config.conf.getConfigValidation(("lion", "threshold")).kwargs["max"])
		similarityThresholdLabelText = _("&Text similarity threshold:")
		self.similarityThresholdEdit = settingsSizerHelper.addLabeledControl(
			similarityThresholdLabelText,
			wx.SpinCtrlDouble,
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
		config.conf["lion"]["interval"] = self.intervalEdit.GetValue()
		config.conf["lion"]["target"] = self.targetList.GetSelection()
		config.conf["lion"]["threshold"] = self.similarityThresholdEdit.GetValue()
