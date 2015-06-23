#!/usr/bin/env python3
from os import path 
import os
import sys
#from setuptools import setup
from distutils.core import setup

here = os.path.dirname(os.path.abspath(__file__))
print (here)
print ("===" *40)
#data_dir = os.path.join(sys.prefix, "local/lib/python2.7/dist-package/cricket_scores/")
data_dir = os.path
data_dir = sys.prefix
print (data_dir)



if(os.path.isfile(sys.prefix + '/local/bin/espn_scrap.py') ):
	os.remove(sys.prefix + '/local/bin/espn_scrap.py')

setup(

	name = "cricscore_indicator",
	version = "3.0.0",
	author = "Nishant Kukreja",
	author_email = "kukreja34@gmail.com",
	description = ("An indicator to show live cricket(domestic/international) scores."),
	license = "GPL",
	keywords = "Cricket Score Live",
	url = "https://github.com/rubyAce71697/cricket-score-applet",
	package_dir = {"cricscores" : "cricketscores"},
	packages = ['cricketscores'],
	include_package_data=True,
	
	data_files = [('cric_icons' ,
		[
			
			
			here + "/cricketscores/icons/0.png",
			here + "/cricketscores/icons/1.png",
			here + "/cricketscores/icons/2.png",
			here + "/cricketscores/icons/3.png",
			here + "/cricketscores/icons/4.png",
			here + "/cricketscores/icons/5.png",
			here + "/cricketscores/icons/6.png",
			here + "/cricketscores/icons/7.png",
			here + "/cricketscores/icons/8.png",
			here + "/cricketscores/icons/9.png",
			here + "/cricketscores/icons/W.png",
			here + "/cricketscores/icons/default_black.png",
			here + "/cricketscores/icons/_.png",
			here + "/cricketscores/icons/won.png",

		]),
		(sys.prefix + '/local/bin',
			[
				here + "/cricketscores/espn_scrap.py"
			])
		
	],



	scripts = ["cricketscores/espn_indicator.py"],

	)


if(os.path.isfile(sys.prefix + '/local/bin/cricket_scores') ):
	os.remove(sys.prefix + '/local/bin/cricket_scores')




os.symlink(sys.prefix + '/local/bin/espn_indicator.py', sys.prefix + '/local/bin/cricket_scores')

