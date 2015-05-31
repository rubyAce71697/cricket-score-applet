"""
    making of "the" fucking awesome applet

    started by Nishant Kukreja(rubyace71697) on 14th May 2015
    improved by Abhishek Rose(rawcoder)

    

    Topic : use espncricinfo.com 's internal website calls to get the score
        summary in json format. 
        No scrapping is done in this module
        It only contains the summary menu 
"""


from gi.repository import Gtk , GObject
from gi.repository import AppIndicator3 as appindicator

import urllib2
from bs4 import BeautifulSoup
import thread
import time
import signal
import json
import requests



REFRESH_TIMEOUT = 5 # second(s)
SRC_WEBSITE = "http://www.espncricinfo.com/"
APP_ID = "new-espn-indicator"

from selenium import webdriver

driver = webdriver.PhantomJS()


GObject.threads_init()



class cric_score_app_menu():
    
    def __init__(self):
        
        
        
        
        self.indicator = appindicator.Indicator.new(APP_ID,
                                        "indicator-messages",
                                        appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.label_disp_index = 0

        # TODO: make menu_setup return the "menu"
        self.menu_setup()
        self.indicator.set_menu(self.menu)
        
    def menu_setup(self):
        self.menu = Gtk.Menu()

        # TODO: merge this with "check_scores"
        r = requests.get("http://www.espncricinfo.com/netstorage/summary.json")
        r= r.json()
        self.menu_item = []
        self.i = 0
        for x in r['matches']:
            #print r['matches'][x]
            self.string = ""
            print
            print str(r['matches'][x]['team1_name']),
            self.string += str(r['matches'][x]['team1_name']).strip().replace('&nbsp;', " ")
            if(str(r['matches'][x]['team1_score']).strip()):
                print "-",
                print str(r['matches'][x]['team1_score']).strip().replace('&nbsp;', " "),
                self.string += str(r['matches'][x]['team1_score']).strip().replace('&nbsp;', " ")
            print "vs",
            self.string += "vs"
            print str(r['matches'][x]['team2_name']).strip(),
            self.string +=str (r['matches'][x]['team2_name']).strip().replace('&nbsp;', " ")
            if(str(r['matches'][x]['team2_score']).strip()):
                print "-",
                print str(r['matches'][x]['team2_score']).strip().replace('&nbsp;', " "),
                self.string += str(r['matches'][x]['team2_score']).strip().replace('&nbsp;', " ")
            #print " " + r['matches'][x]['start_string'],
            if ( 'start_string' in r['matches'][x]):
                print "- " + str(r['matches'][x]['start_string']).replace('&nbsp;', " "),
                self.string += str(r['matches'][x]['start_string']).strip().replace('&nbsp;', " ")
            if( 'start_time' in r['matches'][x]):
                #print " " + str(r['matches'][x]['start_string']).replace('&nbsp;', " ")
                pass
            #self.match_item.append(self.match_info)
            self.menu_item.append(Gtk.MenuItem(self.string))
            #self.menu_item[self.i] = Gtk.MenuItem(self.string)
                   
            #self.submenu.append(Gtk.Menu())
              
            #self.submenu_item.append(Gtk.MenuItem(self.string))
            #self.menu_item[self.i].set_submenu(self.submenu[self.i])
            #self.submenu[self.i].append(self.submenu_item[self.i])
            self.menu_item[self.i].show()
            self.menu.append(self.menu_item[self.i])
            """
                Wait for the change
            """
            self.menu_item[self.i].connect("activate", self.menuitem_response,self.i)
                    
            self.i +=1
                            
                    
            ##print
            ##print


        preferences_item = Gtk.MenuItem("Preferences <dummy>")
        preferences_item.connect("activate", self.preferences)
        preferences_item.show()
        self.menu.append(preferences_item)

        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        quit_item.show()
        self.menu.append(quit_item)
        thread.start_new_thread(self.update_scores, ())
        #thread.start_new_thread(self.update_submenu, ())
    
    
    
    def check_scores(self):
        
        print "Checking latest scores..." + str(self.i)
        
        r = requests.get("http://www.espncricinfo.com/netstorage/summary.json")
        r= r.json()
        start_string = ""
        j =0
        for x in r['matches']:
            #print r['matches'][x]
            self.string = ""
            print
            print str(r['matches'][x]['team1_name']),
            self.string += str(r['matches'][x]['team1_name']).strip().replace('&nbsp;', " ")
            if(str(r['matches'][x]['team1_score']).strip()):
                print "-",
                self.string += " - "
                print str(r['matches'][x]['team1_score']).strip().replace('&nbsp;', " "),
                self.string += str(r['matches'][x]['team1_score']).strip().replace('&nbsp;', " ")
            print "vs",
            self.string += " vs "
            print str(r['matches'][x]['team2_name']).strip(),
            self.string +=str (r['matches'][x]['team2_name']).strip().replace('&nbsp;', " ")
            if(str(r['matches'][x]['team2_score']).strip()):
                print "-",
                self.string += " - "
                print str(r['matches'][x]['team2_score']).strip().replace('&nbsp;', " "),
                self.string += str(r['matches'][x]['team2_score']).strip().replace('&nbsp;', " ")
            
            
            
            if ( 'start_string' in r['matches'][x]):
                print "start_string"
                self.string += " - "
                print "- " + str(r['matches'][x]['start_string']).replace('&nbsp;', " "),
                start_string = str(r['matches'][x]['start_string']).strip().replace('&nbsp;', " ").strip()
                self.string += str(r['matches'][x]['start_string']).strip().replace('&nbsp;', " ")
            
            
            if(not start_string and 'start_time' in r['matches'][x]):
                print "start_time"
                print " " + str(r['matches'][x]['start_time']).replace('&nbsp;', " ")
                self.string += " - "
                self.string += str(r['matches'][x]['start_time']).replace('&nbsp;', " ")
                pass
                ##print "-"*100
        
            if( 'match_clock' in r['matches'][x]):
                self.string += " - begins in - " + str(r['matches'][x]['match_clock']).replace('&nbsp;', " ")
                print " - begins in - " + str(r['matches'][x]['match_clock']).replace('&nbsp;', " ")
                pass

            if( 'result' in r['matches'][x]):
                self.string += " - " + str(r['matches'][x]['result']).replace('&nbsp;', " ")
                print " - " + str(r['matches'][x]['result']).replace('&nbsp;', " ")
                pass
        
            




                # TODO: use glib.idle_add for doing "Gtk" updates inside the "Gtk.main" loop
                #self.menu_item[j].set_label(self.string)
            print "before calling  " + str(j)
            GObject.idle_add(self.set_menu_item , j ,self.string)
            
            #check for updated label
            if( j == self.label_disp_index):
                GObject.idle_add(self.set_indicator_status)
                
            j +=1

                    
        
        
                    
        print 'Updated Scores!!'
        return True

        
    def menuitem_response(self,widget,i):
        self.label_disp_index = i
        self.indicator.set_label(self.menu_item[self.label_disp_index].get_label(),"")
        print 'menuitem_response callbacked'

    def quit(self, widget):
        Gtk.main_quit()

    def preferences(self,widget):
        """
        TODO
        """
        pass

    def update_scores(self):
        while True:
            self.check_scores()
            time.sleep(REFRESH_TIMEOUT-3)
            
    
    
    
    def set_menu_item(self, index , info_string ):
        print "set menu item"
        print "in set_menu_item " + str(index)
        print info_string
        self.menu_item[index].set_label( info_string)

    def set_indicator_status(self):
        print "set indicator status"
        self.indicator.set_label(self.menu_item[self.label_disp_index].get_label(),"")



if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    myIndicator = cric_score_app_menu()
    Gtk.main()
