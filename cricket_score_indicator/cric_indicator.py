#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import gi.repository

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

gi.require_version('Notify', '0.7')
from gi.repository import Notify

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator

import threading
import time
import signal
import webbrowser
import sys

from cricket_score_indicator.espn_scrap import get_matches_summary, get_match_data, DEFAULT_ICON, MATCH_URL_HTML

# the timeout between each fetch
REFRESH_INTERVAL = 10 # second(s)
ICON_PREFIX= "cricscore_indicator-"
ICON_SUFFIX = ""

# DEBUG=1
# from os import path
# ICON_PATH = path.join(path.abspath(path.dirname(__file__)), "..", "icons")
# DARK_ICONS = path.join(ICON_PATH, "dark")
# LIGHT_ICONS = path.join(ICON_PATH, "light")

class CricInd:
    def __init__(self):

        Notify.init("cricket score indicator")
        self.notification = Notify.Notification.new("")
        self.notification.set_app_name("Cricket Score")
        """
        Initialize appindicator and other menus
        """
        self.indicator = appindicator.Indicator.new("cricket-indicator",
                            ICON_PREFIX + DEFAULT_ICON+ ICON_SUFFIX ,
                            appindicator.IndicatorCategory.APPLICATION_STATUS)
        # if DEBUG:
        #     self.indicator.set_icon_theme_path(DARK_ICONS)

        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_label("Loading", "")
        self.indicator.connect("scroll-event", self.scroll_event_cb)
        self.menu_setup()

        # the 'id' of match selected for display as indicator label
        self.label_match_id = None

        self.open_scorecard = set()
        self.intl_menu = []
        self.dom_menu = []

    def main(self):
        """
        Main entry point of execution
        """
        # handle 'C-c'
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.thread = threading.Thread(target=self.main_update_data)
        self.thread.daemon = True
        self.thread.start()

        Gtk.main()

    def menu_setup(self):
        """
        Setup the Gtk self.menu of the indicator
        """
        self.flag = 1
        self.middleClickID = 0
        self.menu = Gtk.Menu.new()

        intl_header = Gtk.MenuItem.new_with_label("INTERNATIONAL")
        intl_header.set_sensitive(False)
        intl_header.show()

        self.menu.append(intl_header)

        intl_sep = Gtk.SeparatorMenuItem.new()
        intl_sep.show()

        self.menu.append(intl_sep)

        dom_header = Gtk.MenuItem.new_with_label("DOMESTIC")
        dom_header.set_sensitive(False)
        dom_header.show()

        self.menu.append(dom_header)

        dom_sep = Gtk.SeparatorMenuItem.new()
        dom_sep.show()

        self.menu.append(dom_sep)

        # separate out matches from "About" and "Quit"
        sep_item = Gtk.SeparatorMenuItem.new()
        sep_item.show()

        # hide our middle-click callback inside the separator
        sep_item.connect("activate", self.middle_click_cb)

        self.menu.append(sep_item)

        # some self promotion
        about_item = Gtk.MenuItem("About")
        about_item.connect("activate", about)
        about_item.show()

        self.menu.append(about_item)

        # if DEBUG:
        #     theme_item = Gtk.MenuItem("Change theme")
        #     theme_item.connect("activate", self.change_icon_theme)
        #     theme_item.show()

        #     self.menu.append(theme_item)

        #we need a way to quit if the indicator is irritating ;-)
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", quit_indicator)
        quit_item.show()

        self.menu.append(quit_item)

        self.indicator.set_menu(self.menu)

        #create menu for middle click
        self.create_scorecard_menu()

        # use the separator's cb for toggling scoreboard
        self.indicator.set_secondary_activate_target(sep_item)

    def create_scorecard_menu(self):
        self.scoreboardMenu = Gtk.Menu.new()
        descriptionItem = Gtk.MenuItem("This is desctiption item")
        scorecardItem = Gtk.MenuItem("This is sorecard")
        commentaryItem = Gtk.MenuItem("Commentary is Loading")
        quitItem = Gtk.MenuItem("Quit")
        aboutItem = Gtk.MenuItem("About")
        toogleItem = Gtk.MenuItem("Back to List")
        quitItem.connect("activate",quit_indicator)
        aboutItem.connect("activate",about)

        self.scoreboardMenu.append(descriptionItem)
        self.scoreboardMenu.append(Gtk.SeparatorMenuItem())

        self.scoreboardMenu.append(scorecardItem)
        self.scoreboardMenu.append(Gtk.SeparatorMenuItem())
        self.scoreboardMenu.append(commentaryItem)

        self.scoreboardMenu.append(Gtk.SeparatorMenuItem())
        self.scoreboardMenu.append(toogleItem)
        self.scoreboardMenu.append(aboutItem)
        self.scoreboardMenu.append(quitItem)
        descriptionItem.show()
        scorecardItem.show()
        commentaryItem.show()
        quitItem.show()
        #toogleItem.show()
        aboutItem.show()
        self.scoreboardMenu.get_children()[1].show()
        self.scoreboardMenu.get_children()[3].show()
        self.scoreboardMenu.get_children()[5].show()




    def middle_click_cb(self, widget):
        if self.label_match_id is None:
            return

        match_item = None
        # linear search FTW
        for i, v in enumerate(self.intl_menu):
            if v['id'] == self.label_match_id:
                match_item = v

                break
        else:
            for i, v in enumerate(self.dom_menu):
                if v['id'] == self.label_match_id:
                    match_item = v
                    break
        if match_item is None:
            return

        # simulate the button-click

        match_item['gtk_check'].set_active(True)
        self.scoreboardMenu.get_children()[0].set_label(match_item['gtk_menu'].get_label())
        self.scoreboardMenu.get_children()[2].set_label(match_item['gtk_scorecard'].get_label())
        self.scoreboardMenu.get_children()[4].set_label(match_item['gtk_commentary'].get_label())


       #    self.indicator.set_menu(self.scoreboardMenu)
        self.scoreboardMenu.popup(None,self.menu,None,None,0,0)







    # def change_icon_theme(self, widget):
    #     if DEBUG:
    #         if self.indicator.get_icon_theme_path() == DARK_ICONS:
    #             self.indicator.set_icon_theme_path(LIGHT_ICONS)
    #         else:
    #             self.indicator.set_icon_theme_path(DARK_ICONS)

    def show_scorecard_cb(self, widget, match_item):
        if widget.get_active():     # ON state
            # remember the 'id' of the match;
            # needed when upstream list is updated
            self.open_scorecard.add(match_item['id'])
            self.expand_submenu(match_item)
        else:                       # OFF state
            if match_item['id'] in self.open_scorecard:
                self.open_scorecard.remove(match_item['id'])
            self.contract_submenu(match_item)

    def contract_submenu(self, match_item):
        match_item['gtk_check'].set_active(False)
        match_item['gtk_description'].hide()
        match_item['gtk_separator_2'].hide()
        match_item['gtk_scorecard'].hide()
        match_item['gtk_separator_3'].hide()
        match_item['gtk_commentary'].hide()
        match_item['gtk_separator_4'].hide()

        match_item['last_ball'] = DEFAULT_ICON   # set to default
        match_item['status'] = ""
        match_item['label_scoreline'] = ""

        # force update in current cycle

        self.update_menu_icon(match_item)
        #GObject.idle_add(match_item['gtk_menu'].set_image,Gtk.Image.new_from_icon_name(ICON_PREFIX + match_item['last_ball'], Gtk.IconSize.BUTTON))
        if match_item['id'] == self.label_match_id:
            self.set_indicator_icon(match_item['last_ball'])
            self.set_indicator_label(match_item['gtk_menu'].get_label())


    def expand_submenu(self, match_item):
        match_item['gtk_check'].set_active(True)
        match_item['gtk_description'].show()
        match_item['gtk_separator_2'].show()
        match_item['gtk_scorecard'].show()
        match_item['gtk_separator_3'].show()
        if match_item['gtk_commentary'].get_label() != "":
            match_item['gtk_commentary'].show()
            match_item['gtk_separator_4'].show()

    def create_match_item(self, match_info):
        match_item = {
                # GTK stuff
                'gtk_menu':                  Gtk.ImageMenuItem.new_with_label(match_info['scoreline']),
                # NOTE: Gtk.ImageMenuItem has been deprecated in GTK 3.10
                'gtk_submenu':               Gtk.Menu.new(),
                'gtk_set_as_label':          Gtk.MenuItem.new_with_label("Set as label"),
                'gtk_description':           Gtk.MenuItem.new_with_label(match_info['description']),
                'gtk_scorecard':             Gtk.MenuItem.new_with_label(match_info['scorecard']),
                'gtk_commentary':            Gtk.MenuItem.new_with_label(match_info['comms']),
                'gtk_check':                 Gtk.CheckMenuItem.new_with_label("Scorecard"),
                'gtk_open_in_browser':       Gtk.MenuItem.new_with_label('Open in browser'),

                'gtk_separator_1':           Gtk.SeparatorMenuItem().new(),
                'gtk_separator_2':           Gtk.SeparatorMenuItem().new(),
                'gtk_separator_3':           Gtk.SeparatorMenuItem().new(),
                'gtk_separator_4':           Gtk.SeparatorMenuItem().new(),

                # our stuff
                'id':                        match_info['id'],
                'url':                       match_info['url'],
                "last_ball":                 match_info['last_ball'],
                "status" :                   match_info['status'],

                #added as part of shortlabel branch
                "label_scoreline":           match_info['label_scoreline']

                }


        match_item['gtk_menu'].set_image(Gtk.Image.new_from_icon_name(ICON_PREFIX + match_info['last_ball'] + ICON_SUFFIX, Gtk.IconSize.BUTTON))
        match_item['gtk_menu'].set_always_show_image(True)

        match_item['gtk_set_as_label'].connect("activate", self.set_as_label_cb, match_item)
        match_item['gtk_description'].set_sensitive(False)
        match_item['gtk_scorecard'].set_sensitive(False)
        match_item['gtk_commentary'].set_sensitive(False)
        match_item['gtk_check'].set_active(False)
        match_item['gtk_check'].connect("toggled", self.show_scorecard_cb, match_item)
        match_item['gtk_open_in_browser'].connect("activate", self.open_in_browser_cb, match_item)

        match_item['gtk_submenu'].append(match_item['gtk_set_as_label'])
        match_item['gtk_submenu'].append(match_item['gtk_separator_1'])
        match_item['gtk_submenu'].append(match_item['gtk_description'])
        match_item['gtk_submenu'].append(match_item['gtk_separator_2'])
        match_item['gtk_submenu'].append(match_item['gtk_scorecard'])
        match_item['gtk_submenu'].append(match_item['gtk_separator_3'])
        match_item['gtk_submenu'].append(match_item['gtk_commentary'])
        match_item['gtk_submenu'].append(match_item['gtk_separator_4'])
        match_item['gtk_submenu'].append(match_item['gtk_check'])
        match_item['gtk_submenu'].append(match_item['gtk_open_in_browser'])

        match_item['gtk_menu'].set_submenu(match_item['gtk_submenu'])

        # everything is "hidden" by default, so we call "show"
        match_item['gtk_menu'].show()
        match_item['gtk_set_as_label'].show()
        match_item['gtk_separator_1'].show()
        match_item['gtk_check'].show()
        match_item['gtk_open_in_browser'].show()

        return match_item

    def set_as_label_cb(self, widget, match_item):
        """
        Callback for 'set as label' menuitem
        """
        # the user has selected this 'm_id' as current label, so we remember it
        self.label_match_id = match_item['id']

        # removed as part of shortlabel branch

        if match_item['label_scoreline']:
            label = match_item['label_scoreline']
        else:
            label = match_item['gtk_menu'].get_label()
        self.set_indicator_label(label )

        self.set_indicator_icon(match_item['last_ball'])


    def scroll_event_cb(self, obj, delta, direction):
        """
        Process scroll-event(s)
        Change indicator label to next/prev in list depending on direction
        """
        if self.label_match_id is None:
            return

        index = -1
        # linear search FTW
        for i, v in enumerate(self.intl_menu):
            if v['id'] == self.label_match_id:
                index = i
                break
        else:
            for i, v in enumerate(self.dom_menu):
                if v['id'] == self.label_match_id:
                    index = len(self.intl_menu) + i
                    break
        if index == -1:
            return

        if direction == Gdk.ScrollDirection.DOWN:
            # activate the button
            (self.intl_menu + self.dom_menu)[(index-1)%len(self.intl_menu+self.dom_menu)]['gtk_set_as_label'].activate()
        else:
            (self.intl_menu + self.dom_menu)[(index+1)%len(self.intl_menu+self.dom_menu)]['gtk_set_as_label'].activate()

    def open_in_browser_cb(self, widget, match_item):
        webbrowser.open(MATCH_URL_HTML(match_item['url']))

    def main_update_data(self):
        while self.flag:
            start = time.time() # get UNIX time
            self.update_labels()
            self.update_sublabels()
            #print self.indicator.get_icon_theme_path()

            duration = time.time() - start # resolution of 1 second is guaranteed
            if duration < REFRESH_INTERVAL:
                # sleep if we still have some time left before website update
                time.sleep(REFRESH_INTERVAL-duration)

    def update_labels(self):
        """
        Fetch the current matches' summary and update the menuitems
        Maybe add or remove menuitems as per the fetched data
        """
        intl_matches, dom_matches = get_matches_summary()
        print intl_matches, dom_matches

        if intl_matches == None:    # request failed! we've got nothing new
            return

        # remove items
        while len(self.intl_menu) > 0 and len(self.intl_menu) > len(intl_matches):
            # GTK updates shouldn't be done in a separate thread,
            # so we add our update to idle queue
            GObject.idle_add(self.remove_menu, (self.intl_menu.pop())['gtk_menu'])

        while len(self.dom_menu) > 0 and len(self.dom_menu) > len(dom_matches):
            GObject.idle_add(self.remove_menu, (self.dom_menu.pop())['gtk_menu'])

        # add items
        while len(self.intl_menu) < len(intl_matches):
            match_item = self.create_match_item(intl_matches[0])
            GObject.idle_add(self.add_menu, match_item['gtk_menu'], 2)  # <-- append after "INTERNATIONAL" header + separator
            self.intl_menu.append(match_item)

        while len(self.dom_menu) < len(dom_matches):
            match_item = self.create_match_item(dom_matches[0])
            GObject.idle_add(self.add_menu, match_item['gtk_menu'], len(self.intl_menu) + 4)    # <-- append after "DOMESTIC" header + separator
            self.dom_menu.append(match_item)

        intl_iter, dom_iter = iter(self.intl_menu), iter(self.dom_menu)
        m_id_set = False
        all_m_id = set()
        for match_info in intl_matches + dom_matches:
            if match_info['intl']:
                intl_item = next(intl_iter)
                intl_item['id'] = match_info['id']
                intl_item['url'] = match_info['url']

                GObject.idle_add(intl_item['gtk_menu'].set_label, match_info['scoreline'])

                curr_item = intl_item
            else:
                dom_item = next(dom_iter)
                dom_item['id'] = match_info['id']
                dom_item['url'] = match_info['url']

                GObject.idle_add(dom_item['gtk_menu'].set_label, match_info['scoreline'])

                curr_item = dom_item

            if match_info['id'] in self.open_scorecard:
                GObject.idle_add(self.expand_submenu, curr_item)
            else:
                GObject.idle_add(self.contract_submenu, curr_item)

            # if current id is set as label
            if not m_id_set and (self.label_match_id is None or match_info['id'] == self.label_match_id):
                self.label_match_id = match_info['id']

                # added in branch shortlabel: Requirement: DD - 170/6 Over(20.0)
                #Logic: if current is set_as_label and open scorecard --> no update will be done since it is updated during updating submenu
                print not match_info['id'] in self.open_scorecard
                print not match_info['label_scoreline']
                """

                {u'team_id': u'3', u'remaining_wickets': u'5', u'event': u'0', u'live_current_name': u'current innings', u'over_limit': u'0.0', u'lead': u'86', u'batted': u'1', u'bowling_team_id': u'2', u'live_current': u'1', u'event_name': None, u'wickets': u'5', u'over_split_limit': u'0.0', u'overs': u'55.0', u'over_limit_run_rate': None, u'runs': u'171', u'balls': u'330', u'remaining_balls': u'0', u'target': u'0', u'remaining_overs': u'0.0', u'innings_number': u'2', u'bpo': u'6', u'required_run_rate': None, u'ball_limit': u'0', u'batting_team_id': u'3', u'run_rate': u'3.10'}

                """

                if not match_info['id'] in self.open_scorecard :
                    label =   match_info['scoreline']
                    print "label while updating: " + label
                    GObject.idle_add(self.set_indicator_label,label)






                """
                    :: removed in shortlabel branch

                print len(self.get_indicator_label().split("  "))
                label +=  "  "  if len(self.get_indicator_label().split("  "))>1 and match_info['id'] in self.open_scorecard else ""
                #label +=  self.get_indicator_label().split(" -- ")[1] if len(self.get_indicator_label().split(" -- ")) else ""
                print len(self.get_indicator_label().split("  ") and match_info['status'])
                if len(self.get_indicator_label().split("  "))>1 and match_info['id'] in self.open_scorecard:
                    label += self.get_indicator_label().split("  ")[1]
                """
                """
                    label in updation:
                """






                m_id_set = True

            all_m_id.add(match_info['id'])

        # don't keep stale m_id's
        self.open_scorecard.intersection_update(all_m_id)

        # we don't want the indicator label to point at old stuff
        if not m_id_set:
            # try setting with intl first
            if len(self.intl_menu) > 0:
                self.label_match_id = self.intl_menu[0]['id']
                GObject.idle_add(self.set_indicator_label, self.intl_menu[0]['gtk_menu'].get_label())
            elif len(self.dom_menu) > 0:
                self.label_match_id = self.dom_menu[0]['id']
                GObject.idle_add(self.set_indicator_label, self.dom_menu[0]['gtk_menu'].get_label())
            # set to default
            else:
                self.label_match_id = None
                GObject.idle_add(self.set_indicator_label, 'Nothings')
                # set the default icon
                GObject.idle_add(self.set_indicator_icon, DEFAULT_ICON)

    def update_sublabels(self):
        """
        update the scorecard, commentary text for each match
        """
        threads = []
        for m in self.intl_menu + self.dom_menu:
            if m['gtk_check'].get_active():
                threads.append(threading.Thread(
                            target=self.update_submenu_data, args=(m,)))
                threads[-1].start()

        for thread in threads:
            thread.join()

    def update_submenu_data(self, match_item):
        match_info = get_match_data(match_item['url'])

        if match_info is None:
            return
        # we've been away for a while, some things may have changed
        if match_item['gtk_check'].get_active():
            match_item['status'] = match_info['status']
            print "match_item status: " + match_item['status']
            match_item['last_ball'] = match_info['last_ball']

            GObject.idle_add(self.update_menu_icon, match_item)
            GObject.idle_add(self.set_submenu_items, match_item, match_info)
            match_item['label_scoreline'] = match_info['label_scoreline']
            if match_item['id'] == self.label_match_id:
                """
                    :: Removed in shortlabel branch
                print len(self.get_indicator_label().split("  "))
                label = self.get_indicator_label().split("  ")[0]
                label += "  " if match_item['status'].strip() else ""
                label += match_item['status'].strip() if match_item['status'].strip() else ""
                """
                #added in shotlabel branch

                if match_item['label_scoreline']:
                    label = match_info['label_scoreline']
                    print "label in updation: " + label
                    GObject.idle_add(self.set_indicator_label,label)
                else:
                    label = match_item['gtk_menu'].get_label()
                    GObject.idle_add(self.set_indicator_label,label)

                GObject.idle_add(self.set_indicator_icon, match_info['last_ball'])
                GObject.idle_add(self.setScoreBoardMenu,match_info)

                if match_item['last_ball'] in ['4','6','W']:

                    self.notification.update(
                    match_item['gtk_menu'].get_label(),
                    match_item['gtk_scorecard'].get_label() + "\n" +    ("\n").join(match_item['gtk_commentary'].get_label().split("\n")[:2]),
                    ICON_PREFIX + match_info['last_ball']  + ICON_SUFFIX


                    )
                    print "for notification : "  + ICON_PREFIX + match_info['last_ball'] + ICON_SUFFIX

                    self.notification.show()
        else:

            match_item['status'] = ""

    ### Helpers
    def set_indicator_label(self, label):
        print "label receivied: " + label
        self.indicator.set_label(label, "Cricket Score Indicator")

    def get_indicator_label(self):
        return self.indicator.get_label()

    def set_indicator_icon(self, icon):
        self.indicator.set_icon(ICON_PREFIX + icon+ ICON_SUFFIX)

    def add_menu(self, widget, pos):
        self.indicator.get_menu().insert(widget, pos)

    def remove_menu(self, widget):
        self.indicator.get_menu().remove(widget)

    def setScoreBoardMenu(self,match_info):
        self.scoreboardMenu.get_children()[0].set_label(match_info['description'])
        self.scoreboardMenu.get_children()[2].set_label(match_info['scorecard'])
        self.scoreboardMenu.get_children()[4].set_label(match_info['comms'])


    def set_submenu_items(self, match_item, match_info):
        match_item['gtk_scorecard'].set_label(match_info['scorecard'])
        match_item['gtk_description'].set_label(match_info['description'])
        match_item['gtk_commentary'].set_label(match_info['comms'])

    def update_menu_icon(self, match_item):
        print ICON_PREFIX + match_item['last_ball']  + ICON_SUFFIX
        match_item['gtk_menu'].set_image(Gtk.Image.new_from_icon_name(ICON_PREFIX + match_item['last_ball'] + ICON_SUFFIX, Gtk.IconSize.BUTTON))

def run():
    """
    The function which should be called to run the indicator
    """
    my_indicator = CricInd()
    my_indicator.main()

def quit_indicator(widget):
    Gtk.main_quit()

def about(widget):
    dialog = Gtk.AboutDialog.new()
    # fixes the "mapped without transient parent" warning
    dialog.set_transient_for(widget.get_parent().get_parent())

    dialog.set_program_name("Cricket Score Indicator")
    dialog.add_credit_section("Authors:", ['Nishant Kukreja (github.com/rubyace71697)', 'Abhishek (github.com/rawcoder)'])
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.set_website("https://github.com/rubyAce71697/cricket-score-applet")
    dialog.set_website_label("Github page")
    dialog.set_comments("Displays live scores from ESPN website in your indicator panel")
    dialog.set_logo_icon_name("cricscore_indicator")

    dialog.run()
    dialog.destroy()

if __name__ == "__main__":
    print ("Use 'cricscore_indicator' to run the applet")
    my_indicator = CricInd()
    my_indicator.main()
