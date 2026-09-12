import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "addon" / "globalPlugins" / "lion" / "sliderMapping.py"


def load_mapping_module():
	spec = importlib.util.spec_from_file_location("sliderMapping", MODULE_PATH)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


class IntervalMappingTests(unittest.TestCase):
	def setUp(self):
		self.mapping = load_mapping_module()

	def test_interval_seconds_to_slider(self):
		self.assertEqual(self.mapping.intervalSecondsToSlider(0.1), 1)
		self.assertEqual(self.mapping.intervalSecondsToSlider(1.0), 10)
		self.assertEqual(self.mapping.intervalSecondsToSlider(10.0), 100)

	def test_slider_to_interval_seconds(self):
		self.assertEqual(self.mapping.sliderToIntervalSeconds(1), 0.1)
		self.assertEqual(self.mapping.sliderToIntervalSeconds(10), 1.0)
		self.assertEqual(self.mapping.sliderToIntervalSeconds(100), 10.0)


class ThresholdMappingTests(unittest.TestCase):
	def setUp(self):
		self.mapping = load_mapping_module()

	def test_threshold_to_slider(self):
		self.assertEqual(self.mapping.thresholdToSlider(0.0), 0)
		self.assertEqual(self.mapping.thresholdToSlider(0.5), 50)
		self.assertEqual(self.mapping.thresholdToSlider(1.0), 100)

	def test_slider_to_threshold(self):
		self.assertEqual(self.mapping.sliderToThreshold(0), 0.0)
		self.assertEqual(self.mapping.sliderToThreshold(50), 0.5)
		self.assertEqual(self.mapping.sliderToThreshold(100), 1.0)


if __name__ == "__main__":
	unittest.main()
