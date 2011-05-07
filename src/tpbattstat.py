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

from gui import Gui
from prefs import Prefs
from battstatus import BattStatus
import sys
import gtk
import gobject
import gnomeapplet

class TPBattStatApplet():
  def __init__(self, applet):
    self.applet = applet

    self.prefs = Prefs(self.applet)
    self.battStatus = BattStatus(self.prefs)
    self.gui = Gui(self.prefs, self.battStatus)

    self.applet.add(self.gui.getGtkWidget())
    self.applet.set_background_widget(self.applet)
    self.applet.show_all()
    
    self.prevDelay = -1
    self.update()

  def update(self):
    self.prefs.update()
    self.battStatus.update()
    self.gui.update()
    if self.prefs.delay != self.prevDelay:
      self.prevDelay = self.prefs.delay
      gobject.timeout_add(self.prefs.delay, self.update)
      return False
    else:
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

