
#!/usr/bin/env python

import sys
import gtk
import gobject
import appindicator
import urllib2
from bs4 import BeautifulSoup
import imaplib
import re
from curses.ascii import isspace
from threading import Thread


from prefrences import PyApp
from bonobo.ui import Widget

PING_FREQUENCY = 1 # seconds

class CheckScore:
    def __init__(self):
        self.label_disp_index = 0
        self.ind = appindicator.Indicator("new-espn-indicator",
                                           "indicator-messages",
                                           appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        #self.ind.set_attention_icon("new-messages-red")
        self.pyapp = PyApp()
        
        ##print "="*100
                
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        ##print "entered again"
        
        self.menu = gtk.Menu()
        self.url = "http://www.espncricinfo.com/"
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

        
        
        self.preferences_item = gtk.MenuItem("Preferences")
        self.preferences_item.connect("activate", self.preferences)
        self.preferences_item.show()
        self.menu.append(self.preferences_item)
            

        
        
        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)
        
        
    def main(self):
        
        #print "code stops in main self"
        self.check_scores() 
        #print "code returns here"      
        """
        while gtk.events_pending():
            #print "in while main self"
            gtk.main_iteration_do(False)
        """
        gobject.timeout_add(PING_FREQUENCY*2000 , self.check_scores)
        #timeout = 1 # 5 minutes
        #gobject.timeout_add(100, self.check_scores)
        #print "code stops after ping"
        self.main()

    def menuitem_response(self,widget,i):
        self.label_disp_index = i
        
    def quit(self, widget):
        sys.exit(0)
        
    def preferences(self,widget):
        self.pyapp.display()
    
    
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
        self.i = 0
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
                    
                    
                    
                    self.menu_item[self.i].set_label(self.string)
                    self.ind.set_label(self.menu_item[self.label_disp_index].get_label())
                    
                    self.i +=1
                    
                   
                    if(self.i == 4):
                        break
        
        
if __name__ == "__main__":
    
    indicator = CheckScore()
    indicator.main()
