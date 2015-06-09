


from gi.repository import Gtk 

class About(Gtk.Window):
    def __init__(self):
        super(About, self).__init__()
        Gtk.Window.__init__(self,title="About")
        Gtk.Window.set_default_size(self,300,150)
        Gtk.Window.set_position(self,Gtk.WindowPosition.CENTER)

        #button1 = Gtk.Button("Hello, World!")
        #button1.set_size_request(40,30)
        #self.add(button1)
        """
        show_submenu = Gtk.CheckButton("Show Submenu")
        update_interval = Gtk.CheckButton("Set upadte interval mannually")
        notify = Gtk.CheckButton("notify of main events")
        show_commentry = Gtk.CheckButton("Show commentry in submenu")
        self.add(show_submenu)
        self.add(update_interval)
        self.add(notify)
        self.add(show_commentry)
        """
        
        hbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL,spacing=0)
        self.add(hbox)
        made_by = Gtk.Label("\nMade By")
        made_by.set_size_request(50,10)
        nishant = Gtk.Label()
        nishant.set_size_request(20,20)
        nishant.set_line_wrap(True)
        nishant.set_justify(Gtk.Justification.CENTER)
        nishant.set_markup("<b>Nishant Kukreja (rubyace71697)</b>")
        abhishek = Gtk.Label()
        abhishek.set_markup("<b>Abhishek Rose (rawcoder)</b>")
        abhishek.set_justify(Gtk.Justification.CENTER)
        hbox.pack_start(made_by,False,False,1)
        hbox.pack_start(nishant, True, True , 1)
        hbox.pack_start(abhishek,True,True,1)
        """
        grid = Gtk.Grid()
        self.add(grid)
        
        made_by = Gtk.Label("\n\nMade By")
        nishant = Gtk.Label()
        nishant.set_markup("<b>Nishant Kukreja (rubyace71697)</b>")
        abhishek = Gtk.Label()
        abhishek.set_markup("<b>Abhishek Rose (rawcoder)</b>")
        grid.attach(made_by,5,5,2,5)
        grid.attach(nishant,5,10, 2, 5)
        grid.attach(abhishek,5,16,2,5)
        """
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
        
        
