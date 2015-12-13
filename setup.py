#!/usr/bin/env python

from distutils.core import setup
import sys

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")

if (sys.version_info[0]*10 + sys.version_info[1]) < 26:
    raise RuntimeError('Sorry, Python < 2.6 is not supported')

setup(
	name             = "cricket_score_indicator",
	version          = "4.0pre",
	author           = "Nishant Kukreja, Abhishek",
	author_email     = "kukreja34@gmail.com",
        maintainer       = "Abhishek",
        maintainer_email = "rawcoder@openmailbox.org",
	description      = "An indicator to show live cricket(domestic/international) scores",
	license          = "GPLv3",
	keywords         = "Cricket Scores Live Indicator Applet AppIndicator Unity GTK",
	url              = "https://github.com/rubyAce71697/cricket-score-applet",
	packages         = ["cricket_score_indicator"],
	package_data     = {"cricket_score_indicator": ["icons/*"]},
	data_files       = [(sys.prefix + "/share/icons/hicolor/scalable/apps", ["cricket_score_indicator/icons/cricscore_indicator.svg"]),
	                    (sys.prefix + "/share/pixmaps", ["cricket_score_indicator/icons/cricscore_indicator.svg"]),
	                    (sys.prefix + "/share/applications", ["cricscore_indicator.desktop"])],
	scripts          = ["cricscore_indicator"],
	long_description = open("README").read(),
        requires         = ["requests", "gi.repository"],
        classifiers      = [
            'Development Status :: 5 - Production/Stable',
            'Programming Language :: Python',
            'Environment :: X11 Applications :: Gnome',
            'Environment :: X11 Applications :: GTK',
            'Environment :: Web Environment',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Topic :: Desktop Environment :: Gnome',
            'Topic :: Internet'
          ]
        )
