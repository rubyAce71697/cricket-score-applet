'''
Created on 06-Jun-2015

@author: nishant
'''

from gi.repository import Gtk , GObject
from gi.repository import AppIndicator3 as appindicator
from espn_scrap import espn_scrap

import urllib2
from bs4 import BeautifulSoup
import thread
import time
import signal
import json
import requests

REFRESH_TIMEOUT = 2 # second(s)
PING_FREQUENCY = 1 # seconds
APP_ID = "new-espn-indicator"


class espn_ind:
    def __init__(self):
        """
        Initialize appindicator and other menus
        """

        # initialize the appindicator
        self.indicator = appindicator.Indicator.new(APP_ID,"indicator-messages",appindicator.IndicatorCategory.APPLICATION_STATUS)

<<<<<<< HEAD
        
=======
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

>>>>>>> 99817f2dc6073b7a4d97dbaa39ea74ec2a401516
        self.scrap = espn_scrap()

        # create the menu and submenu
        self.menu_setup()
        self.indicator.set_menu(self.menu)

        self.label_disp_index = 0

    def menu_setup(self):
        """
        Setup the Gtk menu of the indicator
        """

        self.menu = Gtk.Menu()


        self.match = self.scrap.get_matches_summary()
        self.match_item_menu = []

        i = 0
        for match_info in self.match:
            self.match_item = {}

            # TODO: use consistent naming scheme
            # i.e. prepend 'gtk' or 'menuitem' before gtk objects' names
            self.match_item['label'] = Gtk.MenuItem(match_info['match_score_summary'])
            self.match_item['label_text'] = match_info['match_score_summary']
            self.match_item['url'] = match_info['match_url']

            self.match_item['submenu'] = Gtk.Menu()
            self.match_item['show'] = Gtk.MenuItem("\nSet as Label")
            self.match_item['show'].connect("activate",self.show_clicked,i)

            self.match_item['scorecard'] = Gtk.MenuItem("Loading")
            self.match_item['scorecard'].set_sensitive(False)
            self.match_item['scorecard_text'] = "Loading"

            # attach menuitems and submenu togther as one unit
            self.match_item['submenu'].append(self.match_item['show'])
            self.match_item['submenu'].append(self.match_item['scorecard'])

            self.match_item['label'].set_submenu(self.match_item['submenu'])

            self.menu.append(self.match_item['label'])

            # make a list to keep them all togther
            self.match_item_menu.append(self.match_item)

            self.match_item_menu[i]['label'].show()
            self.match_item_menu[i]['show'].show()
            self.match_item_menu[i]['scorecard'].show()

            i += 1

        self.menu.show_all()

        # you have to attatch the window in future
        self.preferences_item = Gtk.MenuItem("Preferences <beware its not working>")
<<<<<<< HEAD
        
        #self.preferences_item.connect("activate", self.preferences_display)
        
=======

        #self.preferences_item.connect("activate", self.preferences)

>>>>>>> 99817f2dc6073b7a4d97dbaa39ea74ec2a401516
        self.menu.append(self.preferences_item)
        self.preferences_item.show()

        # we need a way to quit if the indicator is irritating ;)
        self.quit_item = Gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)

        self.menu.append(self.quit_item)
        self.quit_item.show()

        while Gtk.events_pending():
            Gtk.main_iteration_do(False)


        thread.start_new_thread(self.update_scores, ())
        thread.start_new_thread(self.update_submenu, ())

    def quit(self, widget):

        Gtk.main_quit()

<<<<<<< HEAD

    def prefrences_show(slef,widget):
        #preferences.display()
        pass
        
=======
>>>>>>> 99817f2dc6073b7a4d97dbaa39ea74ec2a401516
    def show_clicked(self,widget, i):
        self.label_disp_index = i
        GObject.idle_add(self.set_indicator_status)

    def update_scores(self):
        while True:
            self.update_labels()
            time.sleep(REFRESH_TIMEOUT)

    def update_submenu(self):
        while True:
            self.check_submenu()
            time.sleep(REFRESH_TIMEOUT)

    """
    TODO: complete it

    def update_scorecard(self):
        while True:
            update_scorecard_labels()
            time.sleep(REFRESH_TIMEOUT-4)
   """

    def update_labels(self):
        """
            TODO: make a new function for getting the data
        """
        self.match = self.scrap.get_matches_summary()
        j = 0

        for match_info in self.match:
            self.match_item_menu[j]['label_text'] = str(match_info['match_score_summary'])
            self.match_item_menu[j]['url'] = match_info['match_url']

            GObject.idle_add(self.set_menu_item, j, self.match_item_menu[j]['label_text'])

            # update the indicaror status
            if j == self.label_disp_index :
                GObject.idle_add(self.set_indicator_status)

            j += 1

    def set_menu_item(self,index,label_text):
        self.match_item_menu[index]['label'].set_label(label_text)

    def set_indicator_status(self):
        self.indicator.set_label(self.match_item_menu[self.label_disp_index]["label_text"],"")

    def set_submenu_item(self, index , scorecard_text ):
        self.match_item_menu[index]['scorecard'].set_label( scorecard_text)

    def  check_submenu(self):
        match_info = {}
        j = 0

        for match in self.match_item_menu:
            url = "http://www.espncricinfo.com/" + match['url'][1:-5] + ".json?xhr=1"

            match_info = self.scrap.check_match_summary(url,j)
            self.match_item_menu[j]['scorecard_text'] = match_info['match_scorecard_summary']
            GObject.idle_add(self.set_submenu_item , j ,match_info['match_scorecard_summary'])
            j += 1


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    GObject.threads_init()

    myIndicator = espn_ind()
    Gtk.main()
