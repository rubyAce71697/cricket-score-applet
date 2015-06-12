"""
Created on 06-Jun-2015

@author: nishant
"""

from gi.repository import Gtk , GObject
from gi.repository import AppIndicator3 as appindicator
from os import path
import thread
import time
import signal

from espn_scrap import espn_scrap
from about import About

REFRESH_TIMEOUT = 5 # second(s)
APP_ID = "new-espn-indicator"
ICON_PATH = path.join(path.abspath(path.curdir), "screenshots/1.png")

class espn_ind:
    def __init__(self):
        """
        Initialize appindicator and other menus
        """


        # initialize the appindicator
        self.indicator = appindicator.Indicator.new(APP_ID , ICON_PATH , appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.scrap = espn_scrap()
        self.toogle = True
        # create the menu and submenu
        self.label_disp_index = 0
        self.menu_setup()
        self.indicator.set_menu(self.menu)



    def menu_setup(self):
        """
        Setup the Gtk menu of the indicator
        """

        self.menu = Gtk.Menu()


        matches_summary = self.scrap.get_matches_summary()
        self.match_item_menu = []

        i = 0
        for match_info in matches_summary:
            self.match_item = {}




            self.match_item = {

                                'label' : Gtk.ImageMenuItem(Gtk.STOCK_NEW, match_info['score_summary']),
                                'label_text' : match_info['score_summary'],
                                'url' : match_info['url'],
                                'submenu' : Gtk.Menu(),
                                'show' : Gtk.MenuItem("Set as Label"),
                                'description' : "Loading",
                                'match_ball' : "Loading",
                                'gtk_description' : Gtk.MenuItem("Loading"),
                                'scorecard' : Gtk.MenuItem("Loading"),
                                'scorecard_text' : "Loading" ,
                                'gtk_commentary' : Gtk.MenuItem("To be updated"),
                                'commentary_text' : "To be updated",
            }

            self.match_item['show'].connect("activate",self.show_clicked,i)
            self.match_item['scorecard'].set_sensitive(False)
            self.menu.append(self.match_item['label'])
            self.match_item['submenu'].append(self.match_item['show'])
            self.match_item['submenu'].append(self.match_item['gtk_description'])
            self.match_item['submenu'].append(self.match_item['scorecard'])
            self.match_item['submenu'].append(self.match_item['gtk_commentary'])
            self.match_item['label'].set_submenu(self.match_item['submenu'])
            img = Gtk.Image()
            img.set_from_file(path.join(path.abspath(path.curdir), "screenshots/six.png"))
            self.match_item['label'].set_image(img)
            self.match_item['label'].set_always_show_image(True)

            # make a list to keep them all togther
            self.match_item_menu.append(self.match_item)

            self.match_item_menu[i]['label'].show()
            self.match_item_menu[i]['gtk_description'].show()
            self.match_item_menu[i]['show'].show()
            self.match_item_menu[i]['scorecard'].show()
            self.match_item_menu[i]['gtk_commentary'].show()
            i += 1

        #self.menu.show_all()

        #option to show submenu
        self.submenu_item = Gtk.MenuItem("Show SubMenu")
        self.menu.append(self.submenu_item)
        self.submenu_item.show()
        self.submenu_item.connect("activate",self.submenu)

        # you have to attatch the window in future
        self.preferences_item = Gtk.MenuItem("Preferences <beware its not working>")
        self.menu.append(self.preferences_item)
        self.preferences_item.show()

        self.about_item = Gtk.MenuItem("About")
        self.menu.append(self.about_item)
        self.about_item.show()
        self.about_item.connect("activate",self.about)

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

    def about(self,widget):
    	About().display()

    def show_clicked(self,widget, i):
        self.label_disp_index = i
        GObject.idle_add(self.set_indicator_status, self.match_item_menu[i]['match_ball'])

    def submenu(self,widget):
        not self.toogle
        self.preferences_item.hide()

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
        matches_summary = self.scrap.get_matches_summary()
        j = 0

        for match_info in matches_summary:
            self.match_item_menu[j]['label_text'] = str(match_info['score_summary'])
            self.match_item_menu[j]['url'] = match_info['url']

            GObject.idle_add(self.set_menu_item, j, self.match_item_menu[j]['label_text'])

            # update the indicaror status
            if j == self.label_disp_index :
                GObject.idle_add(self.set_indicator_status , self.match_item_menu[j]['match_ball'])

            j += 1

        """
        print "updated menu"
        for x in self.match_item_menu:
            print x
        """

    """
        handlers
    """

    def set_menu_item(self,index,label_text):
        self.match_item_menu[index]['label'].set_label(label_text)

    def set_indicator_status(self, icon_name):
        self.indicator.set_label(self.match_item_menu[self.label_disp_index]["label_text"],"")
        print self.match_item_menu[self.label_disp_index]['url']

        self.indicator.set_icon(path.join(path.abspath(path.curdir), "screenshots", icon_name + ".png"))

    def set_submenu_item(self, index , scorecard_text ):
        self.match_item_menu[index]['scorecard'].set_label( scorecard_text)

    def set_description(self,index, description_text):
        self.match_item_menu[index]['gtk_description'].set_label(description_text)

    def update_icon(self,index, icon_name):
        if icon_name == "":
            # TODO: use a better image
            icon_name = "label_icon"

        #print "update_icon: \"{icon_name}\"".format(icon_name=icon_name)

        img = Gtk.Image()
        img.set_from_file(path.join(path.abspath(path.curdir), "screenshots", icon_name + ".png"))
        self.match_item_menu[index]['label'].set_image(img)

    def set_commentary(self, index, commentary_text):
        self.match_item_menu[index]['gtk_commentary'].set_label(commentary_text)


    def  check_submenu(self):
        """
        print
        print "in espn_indicator.py"
        print "in check_submenu"
        """
        match_info = {}
        j = 0

        for match in self.match_item_menu:
            match_info = self.scrap.get_match_data(j)
            #print match_info
            self.match_item_menu[j]['scorecard_text'] = match_info['scorecard_summary']
            self.match_item_menu[j]['scorecard_summary'] = match_info['scorecard_summary']
            self.match_item_menu[j]['description'] = match_info['description']
            if( match_info['ball'] and match_info['ball'] == '&bull;'):
                match_info['ball'] = '0'
            self.match_item_menu[j]['ball'] = match_info['ball']
            #print match_info['match_ball']

            self.match_item_menu[j]['commentary_text'] = match_info['comms']


            GObject.idle_add(self.update_icon, j , str(match_info['ball']))
            GObject.idle_add(self.set_submenu_item , j ,match_info['scorecard_summary'])
            GObject.idle_add(self.set_description , j ,match_info['description'])
            GObject.idle_add(self.set_commentary, j ,match_info['comms'])

            j += 1

        """
        for x in self.match_item_menu:
            print x
        """



if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    GObject.threads_init()

    myIndicator = espn_ind()
    Gtk.main()
