"""


    started by Nishant Kukreja(rubyace71697) on 14th May 2015
    improved by Abhishek Rose(rawcoder)

"""
from gi.repository import Gtk , GObject
from gi.repository import AppIndicator3 as appindicator

import urllib2
from bs4 import BeautifulSoup
import thread
import time
import signal



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
        self.url = SRC_WEBSITE
        self.content = urllib2.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.content)

        self.para = self.soup.find("div", {"id": "livescores-full" })
        self.para = self.para.find("div", {"id": "live"})

        ##print "-"*100
        self.cat = self.para.findAll("ul", {"class" :"scoreline-list"})
        ##print self.cat
        self.menu_item   = []
        self.string = ""
        self.i = 0
        for x in self.cat:
            ##print "in x"
            self.ulist = x.findAll("li",{ "class":"espni-livescores-scoreline"})
            if(self.ulist):
                #print "in if"
                self.string = ""
                for y in self.ulist:
                    #print "in y"
                    self.string = ""
                    #link = y.find('a')
                    #link = link.get('href')

                    div_int =  y.find("div", {"class":"part-1"})
                    self.string += div_int.find("span", {"class":"team-name"}).get_text().strip() + " "
                    self.string += div_int.find("span", {"class":"team-score"}).get_text().strip() + " "
                    ##print y.find("div", {"class":"part-1"}).get_text(),
                    #if(not (y.find("span", {"class": "versus"}).get_text().strip())):
                    self.string += y.find("span", {"class": "versus"}).get_text().strip() + " "

                    ##print y.find("span", {"class": "versus"}).get_text(),
                    #self.string += y.find("div", {"class":"part-2"}).get_text().strip() + " "
                    div_int =  y.find("div", {"class":"part-2"})
                    self.string += div_int.find("span", {"class":"team-name"}).get_text().strip() + " "
                    self.string += div_int.find("span", {"class":"team-score"}).get_text().strip() + " "

                    ##print y.find("div", {"class":"part-2"}).get_text(),
                    self.string += " --  " +  y.find("span", {"class":"start-time"}).get_text().strip() + " "

                    ##print y.find("span", {"class":"start-time"}).get_text(),

                    #self.menu.append(Gtk.MenuItem(self.menu_item).show())
                    print self.string
                    self.menu_item.append(self.string)
                    self.menu_item[self.i] = Gtk.MenuItem(self.string)
                    self.menu_item[self.i].show()
                    self.menu.append(self.menu_item[self.i])
                    self.menu_item[self.i].connect("activate", self.menuitem_response,self.i)
                    self.i +=1

                    if(self.i == 4):
                        break
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
        print "Checking latest scores..."

        self.url = "http://www.espncricinfo.com/"
        self.content = urllib2.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.content)

        self.para = self.soup.find("div", {"id": "livescores-full" })
        self.para = self.para.find("div", {"id": "live"})

        ##print "-"*100
        self.cat = self.para.findAll("ul", {"class" :"scoreline-list"})
        j = 0
        for x in self.cat:
            ##print "in x"
            self.ulist = x.findAll("li",{ "class":"espni-livescores-scoreline"})
            if(self.ulist):
                ##print "in if"
                self.string = ""
                for y in self.ulist:
                    ##print "in y"
                    self.string = ""

                    div_int =  y.find("div", {"class":"part-1"})
                    self.string += div_int.find("span", {"class":"team-name"}).get_text().strip() + " "
                    self.string += div_int.find("span", {"class":"team-score"}).get_text().strip() + " "
                    ##print y.find("div", {"class":"part-1"}).get_text(),
                    #if(not (y.find("span", {"class": "versus"}).get_text().strip())):
                    self.string += y.find("span", {"class": "versus"}).get_text().strip() + " "

                    ##print y.find("span", {"class": "versus"}).get_text(),
                    #self.string += y.find("div", {"class":"part-2"}).get_text().strip() + " "
                    div_int =  y.find("div", {"class":"part-2"})
                    self.string += div_int.find("span", {"class":"team-name"}).get_text().strip() + " "
                    self.string += div_int.find("span", {"class":"team-score"}).get_text().strip() + " "

                    ##print y.find("div", {"class":"part-2"}).get_text(),
                    self.string += " --  " +  y.find("span", {"class":"start-time"}).get_text().strip() + " "
                    #print self.string



                    # TODO: use glib.idle_add for doing "Gtk" updates inside the "Gtk.main" loop
                    #self.menu_item[j].set_label(self.string)
                    GObject.idle_add(self.set_menu_item , j ,self.string)
                    
                    #check for updated label
                    if( j == self.label_disp_index):
                        GObject.idle_add(self.set_indicator_status)
                    
                    j +=1

                    
                    if(j == 4):
                        break
        
        
        
        
                    
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
            time.sleep(REFRESH_TIMEOUT)
            
    
    
    
    def set_menu_item(self, i , info_string ):
        print "set menu item"
        print info_string
        self.menu_item[i].set_label( info_string)

    def set_indicator_status(self):
        print "set indicator status"
        self.indicator.set_label(self.menu_item[self.label_disp_index].get_label(),"")



if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    myIndicator = cric_score_app_menu()
    Gtk.main()
