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

		valInterval = config.conf.getConfigValidation(("lion", "interval"))
		intervalMin = int(float(valInterval.kwargs["min"]) * 1000)
		intervalMax = int(float(valInterval.kwargs["max"]) * 1000)
		self.intervalEdit = settingsSizerHelper.addLabeledControl(
			_("OCR &interval (ms):"),
			nvdaControls.SelectOnFocusSpinCtrl,
			min=intervalMin,
			max=intervalMax,
			initial=int(config.conf["lion"]["interval"] * 1000),
		)

		self.targetList = settingsSizerHelper.addLabeledControl(
			_("&OCR target:"),
			wx.Choice,
			choices=[
				_("Navigator object"),
				_("Whole Screen"),
				_("current window"),
				_("current control"),
			],
		)
		self.targetList.SetSelection(config.conf["lion"]["target"])

		valThreshold = config.conf.getConfigValidation(("lion", "threshold"))
		thresholdMin = int(float(valThreshold.kwargs["min"]) * 100)
		thresholdMax = int(float(valThreshold.kwargs["max"]) * 100)
		self.similarityThresholdEdit = settingsSizerHelper.addLabeledControl(
			_("&Text similarity threshold (%):"),
			nvdaControls.SelectOnFocusSpinCtrl,
			min=thresholdMin,
			max=thresholdMax,
			initial=int(config.conf["lion"]["threshold"] * 100),
		)

		self.cropUpEdit = settingsSizerHelper.addLabeledControl(_("Crop pixels from &above (%):"), nvdaControls.SelectOnFocusSpinCtrl, min=0, max=100, initial=config.conf["lion"]["cropUp"])
		self.cropDownEdit = settingsSizerHelper.addLabeledControl(_("crop pixels from &below(%):"), nvdaControls.SelectOnFocusSpinCtrl, min=0, max=100, initial=config.conf["lion"]["cropDown"])
		self.cropLeftEdit = settingsSizerHelper.addLabeledControl(_("crop pixels from &left(%):"), nvdaControls.SelectOnFocusSpinCtrl, min=0, max=100, initial=config.conf["lion"]["cropLeft"])
		self.cropRightEdit = settingsSizerHelper.addLabeledControl(_("crop pixels from &right (%):"), nvdaControls.SelectOnFocusSpinCtrl, min=0, max=100, initial=config.conf["lion"]["cropRight"])

		self.regexFiltersEdit = settingsSizerHelper.addLabeledControl(
			_("Regular expression filters (one per &line):"),
			wx.TextCtrl,
			style=wx.TE_MULTILINE,
			size=(-1, 100),
		)
		self.regexFiltersEdit.SetValue(config.conf["lion"].get("regexFilters", ""))
		
		# 核心：拦截按键钩子，防止回车关闭对话框
		self.regexFiltersEdit.Bind(wx.EVT_CHAR_HOOK, self.onRegexKeyHook)

	def onRegexKeyHook(self, event):
		"""处理多行文本框的回车键，确保其换行而不是关闭对话框"""
		keycode = event.GetKeyCode()
		if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
			# 手动插入换行符
			self.regexFiltersEdit.WriteText("\n")
			# 不执行 event.Skip()，从而拦截该事件，不让对话框捕获到回车
			return 
		# 其他按键正常放行
		event.Skip()

	def onSave(self):
		conf = config.conf["lion"]
		conf["cropUp"] = self.cropUpEdit.GetValue()
		conf["cropLeft"] = self.cropLeftEdit.GetValue()
		conf["cropDown"] = self.cropDownEdit.GetValue()
		conf["cropRight"] = self.cropRightEdit.GetValue()
		conf["interval"] = float(self.intervalEdit.GetValue() / 1000)
		conf["target"] = self.targetList.GetSelection()
		conf["threshold"] = float(self.similarityThresholdEdit.GetValue() / 100)
		conf["regexFilters"] = self.regexFiltersEdit.GetValue()