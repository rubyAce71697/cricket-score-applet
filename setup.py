#!/usr/bin/env python3

from distutils.core import setup
import sys

setup(
	name             = "cricket_score_indicator",
	version          = "3.0.0",
	author           = "Nishant Kukreja and Abhishek Rose",
	author_email     = "kukreja34@gmail.com",
	description      = "An indicator to show live cricket(domestic/international) scores",
	license          = "GPL",
	keywords         = "Cricket Scores Live Indicator Applet AppIndicator",
	url              = "https://github.com/rubyAce71697/cricket-score-applet",
	packages         = ["cricket_score_indicator"],
	package_data     = {"cricket_score_indicator": ["icons/*"]},
	data_files       = [(sys.prefix + "/share/icons/hicolor/scalable/apps", ["cricket_score_indicator/icons/cricscore_indicator.svg"]),
	                    (sys.prefix + "/share/pixmaps", ["cricket_score_indicator/icons/cricscore_indicator.svg"]),
	                    (sys.prefix + "/share/applications", ["cricscore_indicator.desktop"])],
	scripts          = ["cricscore_indicator"],
	long_description = open("README.md").read()
        )
