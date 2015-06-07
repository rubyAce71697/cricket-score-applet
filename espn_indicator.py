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

REFRESH_TIMEOUT = 5 # second(s)

GObject.threads_init()


PING_FREQUENCY = 1 # seconds

APP_ID = "new-espn-indicator"


REFRESH_TIMEOUT = 5 # second(s)

GObject.threads_init()


PING_FREQUENCY = 1 # seconds

APP_ID = "new-espn-indicator"

class espn_ind(object):
    

    

    """docstring for espn_ind"""
    
    def __init__(self):
        
        
        
        """
        below will get data from other class
        """
        self.match = []
        self.match_info = {}

        """
        below will constitue the menu and submenu
        """
        self.match_item = {}
        self.match_item_menu = []


        
        self.scrap = espn_scrap()


        
        self.indicator = appindicator.Indicator.new(APP_ID,"indicator-messages",appindicator.IndicatorCategory.APPLICATION_STATUS)
        
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.label_disp_index = 0

        
        self.menu_setup()
        
        
        self.indicator.set_menu(self.menu)
    
    
    def menu_setup(self):
        """
        #print "in espn_ind menu setup"
        """
        self.menu = Gtk.Menu()
        
        self.i = 0

        self.match = self.scrap.check_scores()
        """
        for x in self.match:
            #print "*"*100
            #print x
            #print "-"*100
        """
        for match_info in self.match:
            ##print self.i
            self.match_item = {}
            """
            #print 
            #print
            #print "#"*100
            #print match_info
            
            """

            self.match_item['label'] = Gtk.MenuItem(match_info['match_score_summary'])
            self.match_item['label_text'] = match_info['match_score_summary']
            self.match_item['url'] = match_info['match_url']
            
            self.match_item['submenu'] = Gtk.Menu()
            self.match_item['show'] = Gtk.MenuItem("\nSet as Label")
            self.match_item['show'].connect("activate",self.show_clicked,self.i)

            self.match_item['scorecard'] = Gtk.MenuItem("Loading")
            
            self.match_item['scorecard'].set_sensitive(False)
            self.match_item['scorecard_text'] = "Loading"
            
            """
            #print self.match_item
            """

            """
                attatch menuitems and submenu togther as one unit
            """
            
            self.match_item['submenu'].append(self.match_item['show'])
            
            self.match_item['submenu'].append(self.match_item['scorecard'])
            

            self.match_item['label'].set_submenu(self.match_item['submenu'])
            self.menu.append(self.match_item['label'])

            """
                make a list to keep them all togther 
                otherwise how will you identify them while updating them
            """
            self.match_item_menu.append(self.match_item)
            """
            #print "#printing self.match_item_menu[self.i]"
            #print self.match_item_menu[self.i]
            
            """
            """
                show them
                if not how will they appear
                so its good idea to show them
            """
            """
            self.match_item_menu[self.i].match_item['label'].show()
            self.match_item_menu[self.i].match_item['show'].show()
            self.match_item_menu[self.i].match_item['scorecard'].show()
            """
            self.match_item_menu[self.i]['label'].show()
            self.match_item_menu[self.i]['show'].show()
            self.match_item_menu[self.i]['scorecard'].show()
            
            self.i += 1
            

        

        self.menu.show_all()
        """
            you have to attatch the window in future
        """
        self.preferences_item = Gtk.MenuItem("Preferences <beware its not working>")
        
        #self.preferences_item.connect("activate", self.preferences_display)
        
        self.menu.append(self.preferences_item)
        self.preferences_item.show()
        
        """
            we need a way to quit
            if the indicator is irritating
        """
        self.quit_item = Gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        
        self.menu.append(self.quit_item)
        self.quit_item.show()
        """

        #self.menu_item_submenu.show_all()
        #print "shown all"
        """

        while Gtk.events_pending():
            
            ##print "in while"
            Gtk.main_iteration_do(False)
        """
        #print "Total matches :" + str(self.i)
        """
        

        thread.start_new_thread(self.update_scores, ())
        thread.start_new_thread(self.update_submenu, ())
    

    
    
    def quit(self, widget):

        Gtk.main_quit()


    def prefrences_show(slef,widget):
        #preferences.display()
        pass
        
    def show_clicked(self,widget, i):
        self.label_disp_index = i
        GObject.idle_add(self.set_indicator_status)

    def update_scores(self):
        while True:
            self.update_labels()
            time.sleep(REFRESH_TIMEOUT-3)


    def update_submenu(self):
        #print "update_submenu-"*50
        while True:
            time.sleep(REFRESH_TIMEOUT-3)
            self.check_submenu()
            



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
        self.match = self.scrap.check_scores()
        """
        #print
        for s in self.match:
            #print s

        #print"ends="*100
        j=0
        
        """
        j=0
        
        for match_info in self.match:
            """
            #print j
            
            #self.match_item_menu[j]['label'].set_label(str(match_info['match_summary_score']))
            #print match_info
            """
            self.match_item_menu[j]['label_text'] = str(match_info['match_score_summary'])
            self.match_item_menu[j]['url'] = match_info['match_url']
            
            GObject.idle_add(self.set_menu_item , j ,self.match_item_menu[j]['label_text'])

            
            """
                update the indicaror status
            """
            if j == self.label_disp_index :
                GObject.idle_add(self.set_indicator_status)                
            
            j += 1
            
    def set_menu_item(self,index,label_text):
        self.match_item_menu[index]['label'].set_label(label_text)


    def set_indicator_status(self):
        ##print "set indicator status"
        self.indicator.set_label(self.match_item_menu[self.label_disp_index]["label_text"],"")
    


    def set_submenu_item(self, index , scorecard_text ):
        ##print "set menu item"
        ##print "in set_menu_item " + str(index)
        #print scorecard_text
        self.match_item_menu[index]['scorecard'].set_label( scorecard_text)

    

    def  check_submenu(self):
        match_info = {}
        #print
        #print
        #print "in check_submenu "* 40

        j = 0

        for match in self.match_item_menu:
            #print "in check submenu"
            #print j
            #print match
            
            url = "http://www.espncricinfo.com/" + match['url'][1:-5] + ".json?xhr=1"
            #print url

            match_info = self.scrap.check_match_summary(url,j)
            self.match_item_menu[j]['scorecard_text'] = match_info['match_scorecard_summary']
            GObject.idle_add(self.set_submenu_item , j ,match_info['match_scorecard_summary'])
            j += 1


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    myIndicator = espn_ind()
    Gtk.main()
