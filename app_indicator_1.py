
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



PING_FREQUENCY = 1 # seconds

class CheckScore:
    def __init__(self):
        self.ind = appindicator.Indicator("new-espn-indicator",
                                           "indicator-messages",
                                           appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon("new-messages-red")
        
        
        #print "="*100
                
        self.menu_setup()
        self.ind.set_menu(self.menu)

    def menu_setup(self):
        print "entered again"
        self.menu = gtk.Menu()
        self.url = "http://www.espncricinfo.com/"
        self.content = urllib2.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.content)
        
        self.para = self.soup.find("div", {"id": "livescores-full" })
        self.para = self.para.find("div", {"id": "live"})
        
        #print "-"*100
        self.cat = self.para.findAll("ul", {"class" :"scoreline-list"})
        #print self.cat
        self.menu_item   = []
        self.string = ""
        self.i = 0
        for x in self.cat:
            print "in x"
            self.ulist = x.findAll("li",{ "class":"espni-livescores-scoreline"})
            if(self.ulist):
                print "in if"
                self.string = ""
                for y in self.ulist:
                    print "in y"
                    self.string = ""
                    
                    div_int =  y.find("div", {"class":"part-1"})
                    self.string += div_int.find("span", {"class":"team-name"}).get_text().strip() + " "
                    self.string += div_int.find("span", {"class":"team-score"}).get_text().strip() + " "
                    #print y.find("div", {"class":"part-1"}).get_text(),
                    #if(not (y.find("span", {"class": "versus"}).get_text().strip())):
                    self.string += y.find("span", {"class": "versus"}).get_text().strip() + " "
                    
                    #print y.find("span", {"class": "versus"}).get_text(),
                    #self.string += y.find("div", {"class":"part-2"}).get_text().strip() + " "
                    div_int =  y.find("div", {"class":"part-2"})
                    self.string += div_int.find("span", {"class":"team-name"}).get_text().strip() + " "
                    self.string += div_int.find("span", {"class":"team-score"}).get_text().strip() + " "
                    
                    #print y.find("div", {"class":"part-2"}).get_text(),
                    self.string += " --  " +  y.find("span", {"class":"start-time"}).get_text().strip() + " "
                    
                    #print y.find("span", {"class":"start-time"}).get_text(),
                    
                    #self.menu.append(gtk.MenuItem(self.menu_item).show())
                    self.menu_item.append(self.string)
                    self.menu_item[self.i] = gtk.MenuItem(self.string)
                    self.menu_item[self.i].show()
                    self.menu.append(self.menu_item[self.i])
                    self.i +=1
                    
                    if(self.i == 4):
                        break
                #print
            #print

            

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)
        
        
    def main(self):
        
        print "code stops in main self"
        self.check_scores() 
        print "code returns here"      
        """
        while gtk.events_pending():
            print "in while main self"
            gtk.main_iteration_do(False)
        """
        gobject.timeout_add(PING_FREQUENCY*2000 , self.check_scores)
        #timeout = 1 # 5 minutes
        #gobject.timeout_add(100, self.check_scores)
        print "code stops after ping"
        self.main()

    def quit(self, widget):
        sys.exit(0)
        
    def check_scores(self):
        #for widget in self.menu.get_children():
        #self.menu.remove(widget)
        
        print "code stops in check_scores"
        while gtk.events_pending():
            
            print "in while"
            gtk.main_iteration_do(False)
        
        #self.menu = gtk.Menu()
        
        print "-"*100
        self.url = "http://www.espncricinfo.com/"
        self.content = urllib2.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.content)
        
        self.para = self.soup.find("div", {"id": "livescores-full" })
        self.para = self.para.find("div", {"id": "live"})
        
        #print "-"*100
        self.cat = self.para.findAll("ul", {"class" :"scoreline-list"})
        self.i = 0
        for x in self.cat:
            #print "in x"
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
                    #print y.find("div", {"class":"part-1"}).get_text(),
                    #if(not (y.find("span", {"class": "versus"}).get_text().strip())):
                    self.string += y.find("span", {"class": "versus"}).get_text().strip() + " "
                    
                    #print y.find("span", {"class": "versus"}).get_text(),
                    #self.string += y.find("div", {"class":"part-2"}).get_text().strip() + " "
                    div_int =  y.find("div", {"class":"part-2"})
                    self.string += div_int.find("span", {"class":"team-name"}).get_text().strip() + " "
                    self.string += div_int.find("span", {"class":"team-score"}).get_text().strip() + " "
                    
                    #print y.find("div", {"class":"part-2"}).get_text(),
                    self.string += " --  " +  y.find("span", {"class":"start-time"}).get_text().strip() + " "
                    
                    #print y.find("span", {"class":"start-time"}).get_text(),
                    
                    #self.menu.append(gtk.MenuItem(self.menu_item).show())
                    #self.menu_item[self.i] = (self.string)
                    #self.menu_item[self.i] = gtk.MenuItem(self.string)
                    #self.menu_item[self.i].show()
                    #self.menu.append(self.menu_item[self.i])
                    #self.i +=1
                    print self.string
                    
                    #self.menu_item.append(self.string)
                    
                    if(self.i == 3):
                        self.ind.set_label(self.string)
                    
                    self.menu_item[self.i].set_label(self.string)
                    
                    self.i +=1
                    
                   
                    if(self.i == 4):
                        break
                    
                    #print"code stops after checking i"
        #print "code returns from check-scores"
        """
        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)
        #self.menu.show_all()
        """
        
if __name__ == "__main__":
    print "called gtk main"
    indicator = CheckScore()
    indicator.main()
