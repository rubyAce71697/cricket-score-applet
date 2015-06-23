#!/usr/bin/python3
from gi.repository import Gtk, GObject, GdkPixbuf
from gi.repository import AppIndicator3 as appindicator
import signal

from espn_indicator import espn_ind

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    #GObject.threads_init()     # not needed for GTK version > 3.10

    myIndicator = espn_ind()
    Gtk.main()
