#!/usr/bin/env python
##########################################################################
# TPBattStatApplet v0.1
# Copyright 2011 Elliot Wolk
##########################################################################
# This file is part of TPBattStatApplet.
#
# TPBattStatApplet is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# TPBattStatApplet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TPBattStatApplet. If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import pygtk
pygtk.require('2.0')

from prefs import Prefs
from battstatus import BattStatus
import sys
import gtk, gtk.gdk, gobject
import gnomeapplet

class TPBattStatApplet():
  def __init__(self, applet):
    self.applet = applet
    self.battStatus = BattStatus()
    self.label = gtk.Label("")
    self.applet.add(self.label)
    self.applet.set_background_widget(self.applet)
    self.delay = 0
    self.i = 0
#    self.prefs = Prefs(applet)
    gobject.timeout_add_seconds(2, self.update)
    self.update()
    self.applet.show_all()
        
  def update(self):
    self.battStatus.update()
    self.label.set_text(str(self.i)
      + "-" + self.battStatus.batt0.remaining_percent
      + "-" + self.battStatus.batt1.remaining_percent)
    self.i = self.i + 1
#    self.prefs.update()
    return True



def TPBattStatAppletFactory(applet, iid):
  TPBattStatApplet(applet)
  return True

def main():
  if len(sys.argv) == 2 and sys.argv[1] == "run-in-window":  
    print "running in window"
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("TPBattStatApplet")
    main_window.connect("destroy", gtk.main_quit) 
    app = gnomeapplet.Applet()
    TPBattStatAppletFactory(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()
  else:
    gnomeapplet.bonobo_factory(
      "OAFIID:TPBattStatApplet_Factory", 
      gnomeapplet.Applet.__gtype__, 
      "ThinkPad Battery Status Applet",
      "0",
      TPBattStatAppletFactory)

if __name__ == "__main__":
  sys.exit(main())

