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

REFRESH_TIMEOUT = 5 # second(s)
APP_ID = "espn-indicator"
ICON_PATH = path.join(path.abspath(path.curdir), "screenshots/default_white.png")

class espn_ind:
    def __init__(self):
        """
        Initialize appindicator and other menus
        """

        self.indicator = appindicator.Indicator.new(APP_ID, ICON_PATH, appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.scrap = espn_scrap()

        # TODO: remove toggle
        self.toggle = True
        # create the menu and submenu

        self.label_disp_index = 1
        self.label_clas = 0

        self.menu_setup()

        self.indicator.set_menu(self.menu)

    def menu_setup(self):
        """
        Setup the Gtk menu of the indicator
        """

        self.menu = Gtk.Menu()

        matches_summary = self.scrap.get_matches_summary()
        self.match_menu = []
        self.intl_menu = []
        self.intl_menu.append({
            'label':      Gtk.MenuItem("INTERNATIONAL"),
            'label_text': "INTERNATIONAL", })

        self.intl_menu[0]['label'].set_sensitive(False)

        self.dom_menu = []
        self.dom_menu.append({
            'label':      Gtk.MenuItem("DOMESTIC"),
            'label_text': "DOMESTIC", })
        self.dom_menu[0]['label'].set_sensitive(False)
        intl = 1
        dom = 1

        i = 0
        for match_info in matches_summary:
            self.match_item = {}

            self.match_item = {
                    'label':           Gtk.ImageMenuItem(Gtk.STOCK_NEW, match_info['score_summary']),
                    'label_text':      match_info['score_summary'],
                    'url':             match_info['url'],
                    'submenu':         Gtk.Menu(),
                    'show':            Gtk.MenuItem("Set as Label"),
                    'description':     "Loading",
                    'ball':            "Loading",
                    'gtk_description': Gtk.MenuItem("Loading"),
                    'scorecard':       Gtk.MenuItem("Loading"),
                    'scorecard_text':  "Loading" ,
                    'gtk_commentary':  Gtk.MenuItem("To be updated"),
                    'commentary_text': "To be updated",
                    'international':   match_info['international'],
            }

            self.match_item['show'].connect("activate",self.show_clicked, not match_info['international'],intl,dom, match_info['ball'])
            self.match_item['scorecard'].set_sensitive(False)
            #self.menu.append(self.match_item['label'])
            self.match_item['submenu'].append(self.match_item['show'])
            self.match_item['submenu'].append(self.match_item['gtk_description'])
            self.match_item['submenu'].append(self.match_item['scorecard'])
            self.match_item['submenu'].append(self.match_item['gtk_commentary'])
            self.match_item['label'].set_submenu(self.match_item['submenu'])
            img = Gtk.Image()
            img.set_from_file(path.join(path.abspath(path.curdir), "screenshots/default_white.png"))
            self.match_item['label'].set_image(img)
            self.match_item['label'].set_always_show_image(True)

            # make a list to keep them all togther
            ##self.match_menu.append(self.match_item)
            if(match_info['international']):
                self.intl_menu.append(self.match_item)
                intl+=1
            else:
                self.dom_menu.append(self.match_item)
                dom+=1

            i += 1

        
        self.match_menu.append(self.intl_menu)
        self.match_menu.append(self.dom_menu)
        
        self.intl_menu[0]['label'].show()
        self.dom_menu[0]['label'].show()
        for x in self.match_menu:
            for y in x :
                self.menu.append(y['label'])

        #print self.match_menu
        self.menu.show_all()

        #option to show submenu
        self.submenu_item = Gtk.MenuItem("Hide SubMenu")

        self.menu.append(self.submenu_item)
        self.submenu_item.show()

        self.submenu_item.connect("activate",self.set_submenu_visibile)

        #you have to attatch the window in future
        #self.preferences_item = Gtk.MenuItem("Preferences <beware its not working>")
        #self.menu.append(self.preferences_item)
        #self.preferences_item.show()

        self.about_item = Gtk.MenuItem("About")
        self.menu.append(self.about_item)
        self.about_item.show()
        self.about_item.connect("activate",self.about)

        #we need a way to quit if the indicator is irritating ;)
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

    def about(self,widget):
    	About().display()

    def show_clicked(self,widget, clas, intl, dom, icon_name):
        if not clas:
            self.label_disp_index = intl
        else:
            self.label_disp_index = dom
        
        GObject.idle_add(self.set_indicator_status,clas, icon_name)

    def set_submenu_visibile(self,widget):
        self.toggle = not self.toggle
        if(self.toggle):
            #self.preferences_item.show()
            for match in self.match_menu:
                for category_match in match:
                    if 'submenu' in category_match:
                        category_match['gtk_description'].show()
                        category_match['gtk_commentary'].show()
                        category_match['scorecard'].show()

            self.submenu_item.set_label("Hide Submenu")
            #print self.toggle
        else:
            #self.preferences_item.hide()
            for match in self.match_menu:
                for category_match in match:
                    if 'submenu' in category_match:
                        category_match['gtk_description'].hide()
                        category_match['gtk_commentary'].hide()
                        category_match['scorecard'].hide()

            self.submenu_item.set_label("Show Submenu")

    def update_scores(self):
        while True:
            self.update_labels()
            time.sleep(REFRESH_TIMEOUT)

    def update_submenu(self):
        while True:
            self.check_submenu()
            time.sleep(REFRESH_TIMEOUT)

    def update_labels(self):
        matches_summary = self.scrap.get_matches_summary()
        j = 0
        dom = 1
        intl = 1
        clas = ""

        for match_info in matches_summary:
            # update the indicaror status
            if match_info['international']:
                self.intl_menu[intl]['label_text']= str(match_info['score_summary'])
                self.intl_menu[intl]['url'] = match_info['url']
                self.intl_menu[intl]['international'] = match_info['international']
                clas = 0

                GObject.idle_add(self.set_menu_item, clas,intl, match_info['score_summary'])

                if intl == self.label_disp_index and self.label_clas == clas:
                    GObject.idle_add(self.set_indicator_status , clas , self.intl_menu[intl]['ball'])

                intl += 1
            else:
                self.dom_menu[dom]['label_text'] = str(match_info['score_summary'])
                self.dom_menu[dom]['url'] = match_info['url']
                self.dom_menu[dom]['international'] = match_info['international']
                clas = 1

                GObject.idle_add(self.set_menu_item, clas,dom, match_info['score_summary'])

                if dom == self.label_disp_index and self.label_clas == clas :
                    GObject.idle_add(self.set_indicator_status , clas, self.dom_menu[dom]['ball'] )

                dom += 1

    def set_menu_item(self,clas, index,label_text):
        self.match_menu[clas][index]['label'].set_label(label_text)

    def set_indicator_status(self,clas, icon_name):
        self.label_clas = clas
        self.indicator.set_label(self.match_menu[self.label_clas][self.label_disp_index]['label_text'], "")
        if icon_name == "":
            icon_name = "default_white"
        self.indicator.set_icon(path.join(path.abspath(path.curdir), "screenshots", icon_name + ".png"))

    def set_submenu_item(self, clas, index , scorecard_text ):
        self.match_menu[clas][index]['scorecard'].set_label( scorecard_text)

    def set_description(self,clas, index, description_text):
        self.match_menu[clas][index]['gtk_description'].set_label(description_text)

    def update_icon(self,clas, index, icon_name):
        if icon_name == "":
            icon_name = "default_white"

        #print "update_icon: \"{icon_name}\"".format(icon_name=icon_name)
        img = Gtk.Image()
        img.set_from_file(path.join(path.abspath(path.curdir), "screenshots", icon_name + ".png"))
        self.match_menu[clas][index]['label'].set_image(img)

    def set_commentary(self, clas, index, commentary_text):
        self.match_menu[clas][index]['gtk_commentary'].set_label(commentary_text)

    def  check_submenu(self):
        match_info = {}
        intl = 1
        dom = 1
        j = 0

        for match in self.match_menu:
            for  category_match in match:
                if('url' in category_match):
                    match_info = self.scrap.get_match_data(j)

                    if match_info['international']:
                        self.intl_menu[intl]['scorecard_text']= str(match_info['scorecard_summary'])
                        self.intl_menu[intl]['description'] = match_info['description']
                        self.intl_menu[intl]['international'] = match_info['international']
                        self.intl_menu[intl]['ball'] = match_info['ball']
                        self.intl_menu[intl]['scorecard_summary'] = match_info['scorecard_summary']
                        #print self.intl_menu[intl]
                        clas = 0
                        GObject.idle_add(self.update_icon, clas, intl , str(match_info['ball']))
                        GObject.idle_add(self.set_submenu_item , clas, intl ,match_info['scorecard_summary'])
                        GObject.idle_add(self.set_description , clas, intl ,match_info['description'])
                        GObject.idle_add(self.set_commentary, clas, intl ,match_info['comms'])
                        intl += 1
                    else:
                        self.dom_menu[dom]['scorecard_text']= str(match_info['scorecard_summary'])
                        self.dom_menu[dom]['description'] = match_info['description']
                        self.dom_menu[dom]['international'] = match_info['international']
                        self.dom_menu[dom]['ball'] = match_info['ball']
                        self.dom_menu[dom]['scorecard_summary'] = match_info['scorecard_summary']
                        #print self.dom_menu[dom]
                        clas = 1
                        GObject.idle_add(self.update_icon, clas, dom , str(match_info['ball']))
                        GObject.idle_add(self.set_submenu_item , clas, dom ,match_info['scorecard_summary'])
                        GObject.idle_add(self.set_description , clas, dom ,match_info['description'])
                        GObject.idle_add(self.set_commentary, clas, dom ,match_info['comms'])

                        dom += 1
                    j += 1

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    GObject.threads_init()

    myIndicator = espn_ind()
    Gtk.main()
