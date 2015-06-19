"""
Created on 06-Jun-2015

@author: nishant
"""

from gi.repository import Gtk, GObject
from gi.repository import AppIndicator3 as appindicator

from os import path
import thread
import time
import signal

from espn_scrap import espn_scrap
from about import About

# DO NOT CHANGE; source json changes in 30 seconds (untested), so we aren't missing anything
REFRESH_TIMEOUT = 10 # second(s)
APP_ID = "espn-indicator"
ICON_PATH = path.join(path.abspath(path.curdir), "screenshots/default_white.png")

class espn_ind:
    def __init__(self):
        """
        Initialize appindicator and other menus
        """

        self.indicator = appindicator.Indicator.new(APP_ID,
                                                    ICON_PATH,
                                                    appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.scrap = espn_scrap()

        self.label_disp_index = 0
        self.label_clas = 0

        self.menu = self.menu_setup()
        self.indicator.set_menu(self.menu)

    def menu_setup(self):
        """
        Setup the Gtk menu of the indicator
        """

        menu = Gtk.Menu()

        matches_summary = self.scrap.get_matches_summary()

        intl_menu = []
        dom_menu = []

        intl, dom = 0, 0

        for match_info in matches_summary:
            match_item = {
                    # NOTE: ImageMenuItem has been deprecated since 3.10; TODO: replace it
                    # GTK-stuff
                    'gtk_menu':            Gtk.ImageMenuItem(Gtk.STOCK_NEW, match_info['score_summary']),
                    'gtk_submenu':         Gtk.Menu(),
                    'gtk_show':            Gtk.MenuItem("Set as label"),
                    'gtk_description':     Gtk.MenuItem("Loading"),
                    'gtk_scorecard':       Gtk.MenuItem("Loading"),
                    'gtk_commentary':      Gtk.MenuItem("To be updated"),

                    # meta-stuff
                    'url':                 match_info['url'],

                    # output-stuff
                    # menu
                    'last_ball':           match_info['last_ball'],
                    'label_text':          match_info['score_summary'],
                    # submenu
                    'description_text':    match_info['description'],
                    'scorecard_text':      match_info['score_summary'],
                    'commentary_text':     match_info['comms']
            }

            match_item['gtk_show'].connect("activate",self.show_clicked, match_info['international'], intl, dom, match_info['last_ball'])
            match_item['gtk_description'].set_sensitive(False)
            match_item['gtk_scorecard'].set_sensitive(False)
            match_item['gtk_commentary'].set_sensitive(False)

            match_item['gtk_submenu'].append(match_item['gtk_show'])
            match_item['gtk_submenu'].append(match_item['gtk_description'])
            match_item['gtk_submenu'].append(match_item['gtk_scorecard'])
            match_item['gtk_submenu'].append(match_item['gtk_commentary'])

            match_item['gtk_menu'].set_submenu(match_item['gtk_submenu'])

            img = Gtk.Image()
            img.set_from_file(path.join(path.abspath(path.curdir), "screenshots/default_white.png"))
            # NOTE: both 'set_image' and 'set_always_show_image' have been deprecated; TODO; replace these
            match_item['gtk_menu'].set_image(img)
            match_item['gtk_menu'].set_always_show_image(True)

            if match_info['international']:
                intl_menu.append(match_item)
                intl += 1
            else:
                dom_menu.append(match_item)
                dom += 1

        self.INTL, self.DOM = 0, 1
        self.match_list = intl_menu, dom_menu

        # NOTE: use 'MenuIterm.new()'
        intl_header = Gtk.MenuItem("INTERNATIONAL")
        intl_header.set_sensitive(False)

        menu.append(intl_header)

        for m in self.match_list[self.INTL]:
            menu.append(m['gtk_menu'])

        dom_header = Gtk.MenuItem("DOMESTIC")
        dom_header.set_sensitive(False)

        menu.append(dom_header)

        for m in self.match_list[self.DOM]:
            menu.append(m['gtk_menu'])


        # separate out matches from "About" and "Quit"
        menu.append(Gtk.SeparatorMenuItem.new())

        about_item = Gtk.MenuItem("About")
        about_item.connect("activate",self.about)
        menu.append(about_item)

        #we need a way to quit if the indicator is irritating ;)
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        menu.append(quit_item)

        menu.show_all()

        # TODO: review;
        thread.start_new_thread(self.update_menu, ())
        thread.start_new_thread(self.update_submenu, ())

        return menu

    def quit(self, widget):
        Gtk.main_quit()

    def about(self, widget):
    	About().display()

    def show_clicked(self, widget, intl_flag, intl, dom, icon_name):
        if intl_flag:
            self.label_disp_index = intl
        else:
            self.label_disp_index = dom

        GObject.idle_add(self.set_indicator_status, not intl_flag, icon_name)

    def update_menu(self):
        while True:
            self.update_labels()
            time.sleep(REFRESH_TIMEOUT)

    def update_submenu(self):
        while True:
            self.updates_sublabels()
            time.sleep(REFRESH_TIMEOUT)

    def update_labels(self):
        intl, dom = 0, 0
        matches_summary = self.scrap.get_matches_summary()

        for match_info in matches_summary:
            # update the indicaror status
            if match_info['international']:
                self.match_list[self.INTL][intl]['label_text']= str(match_info['score_summary'])
                self.match_list[self.INTL][intl]['url'] = match_info['url']
                clas = 0

                GObject.idle_add(self.set_menu_item, clas,intl, match_info['score_summary'])

                if intl == self.label_disp_index and self.label_clas == clas:
                    GObject.idle_add(self.set_indicator_status , clas , self.match_list[self.INTL][intl]['last_ball'])

                intl += 1
            else:
                self.match_list[self.DOM][dom]['label_text'] = str(match_info['score_summary'])
                self.match_list[self.DOM][dom]['url'] = match_info['url']
                clas = 1

                GObject.idle_add(self.set_menu_item, clas,dom, match_info['score_summary'])

                if dom == self.label_disp_index and self.label_clas == clas :
                    GObject.idle_add(self.set_indicator_status , clas, self.match_list[self.DOM][dom]['last_ball'] )

                dom += 1

    def set_menu_item(self,clas, index,label_text):
        self.match_list[clas][index]['gtk_menu'].set_label(label_text)

    def set_indicator_status(self, clas, icon_name):
        self.label_clas = clas
        self.indicator.set_label(self.match_list[self.label_clas][self.label_disp_index]['label_text'], "")
        if icon_name == "":
            icon_name = "default_white"
        self.indicator.set_icon(path.join(path.abspath(path.curdir), "screenshots", icon_name + ".png"))

    def set_submenu_items(self, clas, index , scorecard_text, description_text, commentary_text):
        self.match_list[clas][index]['gtk_scorecard'].set_label( scorecard_text)
        self.match_list[clas][index]['gtk_description'].set_label(description_text)
        self.match_list[clas][index]['gtk_commentary'].set_label(commentary_text)

    def update_icon(self,clas, index, icon_name):
        if icon_name == "":
            icon_name = "default_white"

        img = Gtk.Image()
        img.set_from_file(path.join(path.abspath(path.curdir), "screenshots", icon_name + ".png"))
        self.match_list[clas][index]['gtk_menu'].set_image(img)

    def updates_sublabels(self):
        match_info = {}
        intl, dom = 0, 0
        j = 0

        for match in self.match_list:
            for category_match in match:
                if 'url' in category_match:
                    match_info = self.scrap.get_match_data(j)

                    if match_info['international']:
                        self.match_list[self.INTL][intl]['scorecard_text']= str(match_info['scorecard_summary'])
                        self.match_list[self.INTL][intl]['description_text'] = match_info['description']
                        self.match_list[self.INTL][intl]['last_ball'] = match_info['last_ball']
                        self.match_list[self.INTL][intl]['scorecard_summary'] = match_info['scorecard_summary']
                        clas = 0
                        index = intl
                        intl += 1
                    else:
                        self.match_list[self.DOM][dom]['scorecard_text']= str(match_info['scorecard_summary'])
                        self.match_list[self.DOM][dom]['description_text'] = match_info['description']
                        self.match_list[self.DOM][dom]['last_ball'] = match_info['last_ball']
                        self.match_list[self.DOM][dom]['scorecard_summary'] = match_info['scorecard_summary']
                        clas = 1
                        index = dom
                        dom += 1

                    GObject.idle_add(self.update_icon, clas, index , str(match_info['last_ball']))
                    GObject.idle_add(self.set_submenu_items, clas, index, match_info['scorecard_summary'], match_info['description'], match_info['comms'])
                    j += 1

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    #GObject.threads_init()

    myIndicator = espn_ind()
    Gtk.main()
