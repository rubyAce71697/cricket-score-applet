#!/usr/bin/env python2

from distutils.core import setup
import sys
import glob

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")

if (sys.version_info[0]*10 + sys.version_info[1]) < 26:
    raise RuntimeError('Sorry, Python < 2.6 is not supported')

setup(
	name             = "cricket_score_indicator",
	version          = "4.0pre4",
	author           = "Nishant Kukreja, Abhishek",
	author_email     = "kukreja34@gmail.com",
        maintainer       = "Abhishek",
        maintainer_email = "rawcoder@openmailbox.org",
	description      = "An indicator to show live cricket(domestic/international) scores",
	license          = "GPLv3",
	keywords         = "Cricket Scores Live Indicator Applet AppIndicator Unity GTK",
	url              = "https://github.com/rubyAce71697/cricket-score-applet",
	packages         = ["cricket_score_indicator"],
	data_files       = [(sys.prefix + "/share/icons/hicolor/24x24/apps", glob.glob("icons/dark/*")),
	                    (sys.prefix + "/share/icons/ubuntu-mono-dark/apps/24", glob.glob("icons/dark/*")),
	                    (sys.prefix + "/share/icons/ubuntu-mono-light/apps/24", glob.glob("icons/light/*")),
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
