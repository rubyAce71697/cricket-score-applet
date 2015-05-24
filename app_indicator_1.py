#!/usr/bin/env python

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GObject as gobject
import urllib2
from bs4 import BeautifulSoup

PING_FREQUENCY = 1 # second(s)
SRC_WEBSITE = "http://www.espncricinfo.com/"
APP_ID = "new-espn-indicator"
class CheckScore:
    def __init__(self):
        self.indicator = appindicator.Indicator.new(APP_ID,
                                        "indicator-messages",
                                        appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        #self.indicator.set_attention_icon("new-messages-red")

        self.label_disp_index = 0
        ##print "="*100

        # TODO: make menu_setup return the "menu"
        self.menu_setup()
        self.indicator.set_menu(self.menu)

    def menu_setup(self):
        ##print "entered again"

        self.menu = gtk.Menu()

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
                    link = y.find('a')
                    link = link.get('href')

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

                    #self.menu.append(gtk.MenuItem(self.menu_item).show())
                    self.menu_item.append(self.string)
                    self.menu_item[self.i] = gtk.MenuItem(self.string)
                    self.menu_item[self.i].show()
                    self.menu.append(self.menu_item[self.i])
                    self.menu_item[self.i].connect("activate", self.menuitem_response,self.i)
                    self.i +=1

                    if(self.i == 4):
                        break
                ##print
            ##print


        preferences_item = gtk.MenuItem("Preferences <dummy>")
        preferences_item.connect("activate", self.preferences)
        preferences_item.show()
        self.menu.append(preferences_item)

        quit_item = gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        quit_item.show()
        self.menu.append(quit_item)


    def set_timeout(self):
        #gobject.timeout_add(100 , self.check_scores)
            #gobject.threads_init()
            pass

    def main(self):
        #print "code stops in main self"
        #self.check_scores() 
        self.set_timeout()
        #print "code returns here"      

        """
        while gtk.events_pending():
            #print "in while main self"
            gtk.main_iteration_do(False)
        """

        #print "in main"
        #gobject.timeout_add(200 , self.check_scores)
        #timeout = 1 # 5 minutes
        #gobject.timeout_add(100, self.check_scores)
        #print "code stops after ping"

        gtk.main()

    def menuitem_response(self,widget,i):
        self.label_disp_index = i

    def quit(self, widget):
        gtk.main_quit()

    def preferences(self,widget):
        """
        TODO
        """
        pass


    def check_scores(self):
        #for widget in self.menu.get_children():
        #self.menu.remove(widget)

        #print "code stops in check_scores"
        while gtk.events_pending():

            #print "in while"
            gtk.main_iteration_do(False)

        #self.menu = gtk.Menu()

        #print "-"*100
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



                    self.menu_item[j].set_label(self.string)
                    self.indicator.set_label(self.menu_item[self.label_disp_index].get_label())

                    j +=1


                    if(j == 4):
                        break
        return True

if __name__ == "__main__":
    myIndicator = CheckScore()
    myIndicator.main()
