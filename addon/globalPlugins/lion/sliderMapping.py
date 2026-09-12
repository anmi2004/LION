"""Conversion helpers between LION settings values and slider positions."""


def intervalSecondsToSlider(seconds: float) -> int:
	return int(round(seconds * 10))


def sliderToIntervalSeconds(value: int) -> float:
	return value / 10.0


def thresholdToSlider(value: float) -> int:
	return int(round(value * 100))


def sliderToThreshold(value: int) -> float:
	return value / 100.0
