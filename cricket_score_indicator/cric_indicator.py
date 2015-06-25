#!/usr/bin/env python3

from gi.repository import Gtk, GObject, GdkPixbuf
from gi.repository import AppIndicator3 as appindicator

from os import path
import threading
import time
import signal
import sys

from cricket_score_indicator.espn_scrap import espn_scrap

REFRESH_TIMEOUT = 3 # second(s)
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

        thread = threading.Thread(target=self.update_data)
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

        intl_header = Gtk.MenuItem.new_with_label("INTERNATIONAL")
        intl_header.set_sensitive(False)
        intl_header.show()

        self.intl_menu = [ {'gtk_menu':intl_header} ]

        dom_header = Gtk.MenuItem.new_with_label("DOMESTIC")
        dom_header.set_sensitive(False)
        dom_header.show()

        self.dom_menu = [ {'gtk_menu':dom_header} ]

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

        for m in self.intl_menu:
            menu.append(m['gtk_menu'])

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
                # our stuff
                'id':              match_info['id'],
                'url':             match_info['url'],
                }

        match_item['gtk_menu'].set_image(Gtk.Image.new_from_file(ICON_PATH + match_info['last_ball'] + ".png"))
        match_item['gtk_menu'].set_always_show_image(True)

        # OK, this one is not direct
        # we're using the submenu's title for storing indicator's labelling data i.e. score + last ball result + id of the match
        # this is needed because when the user clicks on 'set as label', the callback only gets the corresponding widget's ptr
        # by storing data this we can avoid expensive search operation in the callback
        # see the 'show_clicked' func for more
        match_item['gtk_submenu'].set_title('\n'.join([match_info['score_summary'], match_info['last_ball'], match_info['id']]))
        match_item['gtk_show'].connect("activate",self.show_clicked)

        match_item['gtk_description'].set_sensitive(False)
        match_item['gtk_scorecard'].set_sensitive(False)
        match_item['gtk_commentary'].set_sensitive(False)

        match_item['gtk_submenu'].append(match_item['gtk_show'])
        match_item['gtk_submenu'].append(match_item['gtk_description'])
        match_item['gtk_submenu'].append(match_item['gtk_scorecard'])
        match_item['gtk_submenu'].append(match_item['gtk_commentary'])

        match_item['gtk_menu'].set_submenu(match_item['gtk_submenu'])

        match_item['gtk_menu'].show_all()

        return match_item

    def quit(self, widget):
        Gtk.main_quit()



    def about(self, widget):
    	dialog = Gtk.AboutDialog.new()
    	# fixes the "mapped without transient parent" warning
    	dialog.set_transient_for(widget.get_parent().get_parent())

    	dialog.set_program_name("ESPN Indicator")
    	dialog.add_credit_section("Authors:", ['Nishant Kukreja (github.com/rubyace71697)', 'Abhishek Rose (github.com/rawcoder)'])
    	dialog.set_license_type(Gtk.License.GPL_3_0)
    	dialog.set_website("https://github.com/rubyAce71697/cricket-score-applet")
    	dialog.set_website_label("Github page")
    	dialog.set_comments("Displays live scores from ESPN website in your indicator panel")
    	dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(ICON_PATH + "default_black" + ".png"))

    	dialog.run()
    	dialog.destroy()

    def show_clicked(self, widget):
        """
        Callback for 'set as label' menuitem
        """
        # retriveve the stored data from submenu, 'set as label' menuitem's parent
        label, icon, m_id = widget.get_parent().get_title().split('\n')

        # the user has selected this 'm_id' as current label, so we remember it
        self.ind_label_match_id = m_id
        self.set_indicator_label(label)
        self.set_indicator_icon(icon)

    def set_indicator_label(self, label):
        self.indicator.set_label(label, "")

    def set_indicator_icon(self, icon):
        self.indicator.set_icon(ICON_PATH + icon + ".png")

    def update_data(self):
        while True:
            #print("Updating stuff")
            self.update_labels()
            self.update_sublabels()
            #print("...  done")
            #no need to add sleep already it is slow

    def update_labels(self):
        """
        Fetch the current matches' summary and update the menuitems
        may be add or remove menuitems as per the fetched data
        """
        intl_matches, dom_matches = self.scrap.get_matches_summary()

        # remove items
        while len(self.intl_menu) > 1 and len(self.intl_menu)-1 > len(intl_matches):
            # GTK updates shouldn't be done in a separate thread, so we add our update to idle queue
            GObject.idle_add(self.remove_menu, (self.intl_menu.pop())['gtk_menu'])

        while len(self.dom_menu) > 1 and len(self.dom_menu)-1 > len(dom_matches):
            GObject.idle_add(self.remove_menu, (self.dom_menu.pop())['gtk_menu'])

        # add items
        while len(self.intl_menu)-1 < len(intl_matches):
            match_item = self.create_match_item(intl_matches[0])
            GObject.idle_add(self.add_menu, match_item['gtk_menu'], 1)
            self.intl_menu.append(match_item)

        while len(self.dom_menu)-1 < len(dom_matches):
            match_item = self.create_match_item(dom_matches[0])
            GObject.idle_add(self.add_menu, match_item['gtk_menu'], len(self.intl_menu) + 1)
            self.dom_menu.append(match_item)

        intl, dom = 1, 1
        m_id_set = False
        for match_info in intl_matches + dom_matches:
            if match_info['international']:
                self.intl_menu[intl]['id'] = match_info['id']
                self.intl_menu[intl]['url'] = match_info['url']

                GObject.idle_add(self.set_menu_label, self.intl_menu[intl]['gtk_menu'], match_info['score_summary'])

                intl += 1
            else:
                self.dom_menu[dom]['id'] = match_info['id']
                self.dom_menu[dom]['url'] = match_info['url']

                GObject.idle_add(self.set_menu_label, self.dom_menu[dom]['gtk_menu'], match_info['score_summary'])

                dom += 1

            if self.ind_label_match_id is None or match_info['id'] == self.ind_label_match_id:
                GObject.idle_add(self.set_indicator_label, match_info['score_summary'])
                m_id_set = True

        # we don't want the indicator label to point at old stuff
        if not m_id_set:
            if len(self.intl_menu) > 1:
                self.ind_label_match_id = self.intl_menu[1]['id']
                GObject.idle_add(self.set_indicator_label, self.intl_menu[1]['gtk_menu'].get_label())
            elif len(self.dom_menu) > 1:
                self.ind_label_match_id = self.dom[1]['id']
                GObject.idle_add(self.set_indicator_label, self.dom_menu[1]['gtk_menu'].get_label())
            else:
                self.ind_label_match_id = None
                GObject.idle_add(self.set_indicator_label, "Nothings")

    def update_sublabels(self):
        """
        update the scorecard, commentary text for each match
        """
        for m in self.intl_menu[1:] + self.dom_menu[1:]:
            threading.Thread(target = self.update_menu_data, args = m).start()

    def update_menu_data(self, m):
        match_info = self.scrap.get_match_data(m['id'])

        #maybe lost connection or something bad happened
        if match_info == {}:
            return

        # used when 'set_as_label' button is clicked
        m['gtk_submenu'].set_title('\n'.join([match_info['score_summary'], match_info['last_ball'], match_info['id']]))

        if('won by' in match_info['scorecard_summary']):
            match_info['last_ball'] = "won"

        GObject.idle_add(self.update_menu_icon, m['gtk_menu'], match_info['last_ball'])
        GObject.idle_add(self.set_submenu_items, m, match_info['scorecard_summary'], match_info['description'], match_info['comms'])
        if match_info['id'] == self.ind_label_match_id:
            GObject.idle_add(self.set_indicator_icon, match_info['last_ball'])

    def add_menu(self, widget, pos):
        widget.show()
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
