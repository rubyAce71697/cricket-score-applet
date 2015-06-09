'''
Created on 15-May-2015

@author: nishant
'''
from gi.repository import Gtk 

class Preferences(Gtk.Window):
    def __init__(self):
        super(Preferences, self).__init__()
        Gtk.Window.__init__(self,title="Preferences")
        Gtk.Window.set_default_size(self,400,325)
        Gtk.Window.set_position(self,Gtk.WindowPosition.CENTER)

        #button1 = Gtk.Button("Hello, World!")
        #button1.set_size_request(40,30)
        #self.add(button1)

        show_submenu = Gtk.CheckButton("Show Submenu")
        update_interval = Gtk.CheckButton("Set upadte interval mannually")
        notify = Gtk.CheckButton("notify of main events")
        show_commentry = Gtk.CheckButton("Show commentry in submenu")
        self.add(show_submenu)
        self.add(update_interval)
        self.add(notify)
        self.add(show_commentry)

        """

        self.set_title("Preferences")
        
        btn1 = gtk.Button("Button")
        btn1.set_sensitive(False)
        btn2 = gtk.Button("Button")
        btn3 = gtk.Button(stock=gtk.STOCK_CLOSE)
        btn4 = gtk.Button("Button")
        btn4.set_size_request(80, 40)

        fixed = gtk.Fixed()
        fixed.put(btn1, 20, 30)
        fixed.put(btn2, 100, 30)
        fixed.put(btn3, 20, 80)
        fixed.put(btn4, 100, 80)
        self.add(fixed)
        #self.show_all()
        
        
        self.connect("destroy",gtk.main_quit)
        self.set_size_request(250,150)
        self.set_position(gtk.WIN_POS_CENTER)
        
        """
    def display(self):
        self.show_all();
        Gtk.main()
        
        
        
#PyApp()
#gtk.main()