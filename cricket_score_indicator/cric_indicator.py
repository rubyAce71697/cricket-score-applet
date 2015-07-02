#!/usr/bin/env python

from gi.repository import Gtk, GObject, GdkPixbuf
from gi.repository import AppIndicator3 as appindicator
#from gi.repository import Dbusmenu

from os import path
import threading
import time
import signal
import sys

from cricket_score_indicator.espn_scrap import espn_scrap

# the timeout between each fetch
REFRESH_INTERVAL = 10 # second(s)
ICON_PATH = path.join(path.abspath(path.dirname(__file__)), "icons/")

class cric_ind:
    def __init__(self):
        """
        Initialize appindicator and other menus
        """

        self.indicator = appindicator.Indicator.new("cricket-indicator",
                                                ICON_PATH + "default_white.png",
                                                appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        self.scrap = espn_scrap()

        # the 'id' of match selected for display as indicator label
        self.ind_label_match_id = None
        self.indicator.set_label("Loading", "")

        self.menu = self.menu_setup()
        self.indicator.set_menu(self.menu)

        thread = threading.Thread(target=self.main_update_data)
        thread.daemon = True
        thread.start()

    def main(self):
        # handle 'C-c'
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

    def menu_setup(self):
        """
        Setup the Gtk menu of the indicator
        """

        self.intl_menu = [ ]
        self.dom_menu = [ ]

        intl_matches, dom_matches = self.scrap.get_matches_summary()
        for match_info in intl_matches + dom_matches:
            match_item = self.create_match_item(match_info)

            if match_info['international']:
                self.intl_menu.append(match_item)
            else:
                self.dom_menu.append(match_item)

            if self.ind_label_match_id is None:
                self.ind_label_match_id = match_info['id']

        menu = Gtk.Menu.new()

        intl_header = Gtk.MenuItem.new_with_label("INTERNATIONAL")
        intl_header.set_sensitive(False)
        intl_header.show()

        menu.append(intl_header)

        intl_sep = Gtk.SeparatorMenuItem.new()
        intl_sep.show()

        menu.append(intl_sep)

        for m in self.intl_menu:
            menu.append(m['gtk_menu'])

        dom_header = Gtk.MenuItem.new_with_label("DOMESTIC")
        dom_header.set_sensitive(False)
        dom_header.show()

        menu.append(dom_header)

        dom_sep = Gtk.SeparatorMenuItem.new()
        dom_sep.show()

        menu.append(dom_sep)

        for m in self.dom_menu:
            menu.append(m['gtk_menu'])

        # separate out matches from "About" and "Quit"
        sep_item = Gtk.SeparatorMenuItem.new()
        sep_item.show()

        menu.append(sep_item)

        # some self promotion
        about_item = Gtk.MenuItem("About")
        about_item.connect("activate",self.about)
        about_item.show()

        menu.append(about_item)

        #we need a way to quit if the indicator is irritating ;)
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.quit)
        quit_item.show()

        menu.append(quit_item)

        return menu

    def create_match_item(self, match_info):
        match_item = {
                # GTK stuff
                'gtk_menu':        Gtk.ImageMenuItem.new_with_label(match_info['score_summary']),
                # NOTE: Gtk.ImageMenuItem has been deprecated in GTK 3.10
                'gtk_submenu':     Gtk.Menu.new(),
                'gtk_show':        Gtk.MenuItem.new_with_label("Set as label"),
                'gtk_description': Gtk.MenuItem.new_with_label(match_info['description']),
                'gtk_scorecard':   Gtk.MenuItem.new_with_label(match_info['scorecard_summary']),
                'gtk_commentary':  Gtk.MenuItem.new_with_label(match_info['comms']),
                'gtk_check':       Gtk.CheckMenuItem.new_with_label("Scorecard"),

                'gtk_seperator_1': Gtk.SeparatorMenuItem().new(),
                'gtk_seperator_2': Gtk.SeparatorMenuItem().new(),
                'gtk_seperator_3': Gtk.SeparatorMenuItem().new(),
                'gtk_seperator_4': Gtk.SeparatorMenuItem().new(),

                # our stuff
                'id':              match_info['id'],
                'url':             match_info['url'],
                "last_ball":       match_info['last_ball'],
                }

        match_item['gtk_menu'].set_image(Gtk.Image.new_from_file(ICON_PATH + match_info['last_ball'] + ".png"))
        match_item['gtk_menu'].set_always_show_image(True)

        match_item['gtk_show'].connect("activate", self.show_clicked, match_item)
        match_item['gtk_description'].set_sensitive(False)
        match_item['gtk_scorecard'].set_sensitive(False)
        match_item['gtk_commentary'].set_sensitive(False)
        match_item['gtk_check'].set_active(False)
        match_item['gtk_check'].connect("toggled", self.local_enable, match_item)

        match_item['gtk_submenu'].append(match_item['gtk_show'])
        match_item['gtk_submenu'].append(match_item['gtk_seperator_1'])
        match_item['gtk_submenu'].append(match_item['gtk_description'])
        match_item['gtk_submenu'].append(match_item['gtk_seperator_2'])
        match_item['gtk_submenu'].append(match_item['gtk_scorecard'])
        match_item['gtk_submenu'].append(match_item['gtk_seperator_3'])
        match_item['gtk_submenu'].append(match_item['gtk_commentary'])
        match_item['gtk_submenu'].append(match_item['gtk_seperator_4'])
        match_item['gtk_submenu'].append(match_item['gtk_check'])

        match_item['gtk_menu'].set_submenu(match_item['gtk_submenu'])

        match_item['gtk_menu'].show()
        match_item['gtk_show'].show()
        match_item['gtk_seperator_1'].show()
        match_item['gtk_check'].show()

        return match_item

    def quit(self, widget):
        Gtk.main_quit()

    def about(self, widget):
    	dialog = Gtk.AboutDialog.new()
    	# fixes the "mapped without transient parent" warning
    	dialog.set_transient_for(widget.get_parent().get_parent())

    	dialog.set_program_name("Cricket Score Indicator")
    	dialog.add_credit_section("Authors:", ['Nishant Kukreja (github.com/rubyace71697)', 'Abhishek Rose (github.com/rawcoder)'])
    	dialog.set_license_type(Gtk.License.GPL_3_0)
    	dialog.set_website("https://github.com/rubyAce71697/cricket-score-applet")
    	dialog.set_website_label("Github page")
    	dialog.set_comments("Displays live scores from ESPN website in your indicator panel")
    	dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(ICON_PATH + "cricscore_indicator" + ".svg"))

    	dialog.run()
    	dialog.destroy()

    def local_enable(self, widget, match_item):
        if widget.get_active():
            self.show_submenu(match_item)
        else:
            self.hide_submenu(match_item)

    def hide_submenu(self, match_item):
        match_item['gtk_description'].hide()
        match_item['gtk_seperator_2'].hide()
        match_item['gtk_scorecard'].hide()
        match_item['gtk_seperator_3'].hide()
        match_item['gtk_commentary'].hide()
        match_item['gtk_seperator_4'].hide()

        match_item['last_ball'] = "_"   # set to default

        # force update in current cycle
        self.update_menu_icon(match_item['gtk_menu'], "_")  # default icon

        if match_item['id'] == self.ind_label_match_id:
            self.set_indicator_icon('_')

    def show_submenu(self,match_item):
        match_item['gtk_description'].show()
        match_item['gtk_seperator_2'].show()
        match_item['gtk_scorecard'].show()
        match_item['gtk_seperator_3'].show()
        match_item['gtk_commentary'].show()
        match_item['gtk_seperator_4'].show()

    def show_clicked(self, widget, match_item):
        """
        Callback for 'set as label' menuitem
        """
        # the user has selected this 'm_id' as current label, so we remember it
        self.ind_label_match_id = match_item['id']

        self.set_indicator_label(match_item['gtk_menu'].get_label())
        self.set_indicator_icon(match_item['last_ball'])

    def main_update_data(self):
        while True:
            start = time.time() # get UNIX time
            #sys.stderr.write("\nUpdating stuff")
            self.update_labels()
            self.update_sublabels()
            #sys.stderr.write("...  done")

            duration = time.time() - start # resolution of 1 second is guaranteed
            if duration < REFRESH_INTERVAL: # sleep if we still have some time left before website update
                time.sleep(REFRESH_INTERVAL-duration)

    def update_labels(self):
        """
        Fetch the current matches' summary and update the menuitems
        may be add or remove menuitems as per the fetched data
        """
        intl_matches, dom_matches = self.scrap.get_matches_summary()

        # remove items
        while len(self.intl_menu) > 0 and len(self.intl_menu) > len(intl_matches):
            # GTK updates shouldn't be done in a separate thread, so we add our update to idle queue
            GObject.idle_add(self.remove_menu, (self.intl_menu.pop())['gtk_menu'])

        while len(self.dom_menu) > 0 and len(self.dom_menu) > len(dom_matches):
            GObject.idle_add(self.remove_menu, (self.dom_menu.pop())['gtk_menu'])

        # add items
        while len(self.intl_menu) < len(intl_matches):
            match_item = self.create_match_item(intl_matches[0])
            GObject.idle_add(self.add_menu, match_item['gtk_menu'], 1)  # <-- append after "INTERNATIONAL" header
            self.intl_menu.append(match_item)

        while len(self.dom_menu) < len(dom_matches):
            match_item = self.create_match_item(dom_matches[0])
            GObject.idle_add(self.add_menu, match_item['gtk_menu'], len(self.intl_menu) + 2)    # <-- append after "DOMESTIC" header
            self.dom_menu.append(match_item)

        intl_iter, dom_iter = iter(self.intl_menu), iter(self.dom_menu)
        m_id_set = False
        for match_info in intl_matches + dom_matches:
            if match_info['international']:
                intl_item = intl_iter.next()

                intl_item['id'] = match_info['id']
                intl_item['url'] = match_info['url']

                GObject.idle_add(self.set_menu_label, intl_item['gtk_menu'], match_info['score_summary'])
            else:
                dom_item = dom_iter.next()

                dom_item['id'] = match_info['id']
                dom_item['url'] = match_info['url']

                GObject.idle_add(self.set_menu_label, dom_item['gtk_menu'], match_info['score_summary'])

            if self.ind_label_match_id is None or match_info['id'] == self.ind_label_match_id:
                GObject.idle_add(self.set_indicator_label, match_info['score_summary'])
                m_id_set = True

        # we don't want the indicator label to point at old stuff
        if not m_id_set:
            if len(self.intl_menu) > 0:
                self.ind_label_match_id = self.intl_menu[1]['id']
                GObject.idle_add(self.set_indicator_label, self.intl_menu[0]['gtk_menu'].get_label())
            elif len(self.dom_menu) > 0:
                self.ind_label_match_id = self.dom[1]['id']
                GObject.idle_add(self.set_indicator_label, self.dom_menu[0]['gtk_menu'].get_label())
            else:
                self.ind_label_match_id = None
                GObject.idle_add(self.set_indicator_label, "Nothings")
            # set the default icon
            GObject.idle_add(self.set_indicator_icon, "_")

    def update_sublabels(self):
        """
        update the scorecard, commentary text for each match
        """
        threads = []
        for m in self.intl_menu + self.dom_menu:
            if m['gtk_check'].get_active():
                threads.append(threading.Thread(target = self.update_submenu_data, args = (m,)))
                threads[-1].start()

        for thread in threads:
            thread.join()

    def update_submenu_data(self, m):
        match_info = self.scrap.get_match_data(m['id'])

        #maybe lost connection or something bad happened
        if match_info == {}:
            return

        # we've been away for a while, some things may have changed
        if m['gtk_check'].get_active():
            m['last_ball'] = match_info['last_ball']

            if 'won by' in match_info['scorecard_summary']:
                match_info['last_ball'] = "won"

            GObject.idle_add(self.update_menu_icon, m['gtk_menu'], match_info['last_ball'])
            GObject.idle_add(self.set_submenu_items, m, match_info['scorecard_summary'], match_info['description'], match_info['comms'])

            if match_info['id'] == self.ind_label_match_id:
                GObject.idle_add(self.set_indicator_icon, match_info['last_ball'])

    ### Helpers
    def set_indicator_label(self, label):
        self.indicator.set_label(label, "Cricket Score Indicator")

    def set_indicator_icon(self, icon):
        self.indicator.set_icon(ICON_PATH + icon + ".png")

    def add_menu(self, widget, pos):
        self.menu.insert(widget, pos)

    def remove_menu(self, widget):
        self.menu.remove(widget)

    def set_menu_label(self, widget, label):
        widget.set_label(label)

    def set_submenu_items(self, match_item, scorecard_text, description_text, commentary_text):
        match_item['gtk_scorecard'].set_label( scorecard_text)
        match_item['gtk_description'].set_label(description_text)
        match_item['gtk_commentary'].set_label(commentary_text)

    def update_menu_icon(self, widget, icon):
        widget.set_image(Gtk.Image.new_from_file(ICON_PATH + icon + ".png"))

def run():
    myIndicator = cric_ind()
    myIndicator.main()

if __name__ == "__main__":
    print ("Use 'cricscore_indicator' to run the applet")
