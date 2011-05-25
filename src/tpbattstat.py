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
from prefs import Prefs, SCHEMA_DIR
from battstatus import BattStatus
from dzenprinter import DzenPrinter
import sys
import gtk
import gobject
import gnomeapplet
import time
import socket

class TPBattStatApplet():
  def __init__(self, applet, mode="gtk", forceDelay=None):
    self.applet = applet
    self.mode = mode
    self.forceDelay = forceDelay

    if self.applet == None:
      gconf_root_key = None
    else:
      gconf_root_key = self.applet.get_preferences_key()
    self.prefs = Prefs(gconf_root_key)
    self.battStatus = BattStatus(self.prefs)
    if self.mode == "gtk":
      self.gui = Gui(self.applet, self.prefs, self.battStatus)
      self.applet.add_preferences(SCHEMA_DIR)
      self.applet.add(self.gui.getGtkWidget())
      self.applet.set_background_widget(self.applet)
      self.applet.show_all()
    elif self.mode == "dzen":
     self.dzenprinter = DzenPrinter(self.prefs, self.battStatus)

  def startUpdate(self):
    self.curDelay = -1
    self.update()
  def update(self):
    self.prefs.update()
    if self.forceDelay != None:
      self.prefs.delay = self.forceDelay
    self.battStatus.update()

    if self.mode == "gtk":
      self.gui.update()
    elif self.mode == "dzen":
      try:
        print self.dzenprinter.getDzenMarkup()
        sys.stdout.flush()
      except IOError, e:
        print >> sys.stderr, "STDOUT is broken, assuming dzen is dead"
        sys.exit(1)

    if self.prefs.delay != self.curDelay:
      self.curDelay = self.prefs.delay
      if self.curDelay <= 0:
        self.curDelay = 1000
      gobject.timeout_add(self.curDelay, self.update)
      return False
    else:
      return True

def TPBattStatAppletFactory(applet, iid):
  tpbattstat = TPBattStatApplet(applet)
  tpbattstat.startUpdate()
  return True

def main():
  if len(sys.argv) == 2 and sys.argv[1] == "run-in-window":
    print "running in window"
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title("TPBattStatApplet")
    main_window.connect("destroy", gtk.main_quit) 
    applet = gnomeapplet.Applet()
    TPBattStatAppletFactory(applet, None)
    applet.reparent(main_window)
    main_window.show_all()
    gtk.main()
    sys.exit()
  elif (len(sys.argv) == 2 or len(sys.argv) == 3) and sys.argv[1] == "--dzen":
    if len(sys.argv) == 3:
      tpbattstat = TPBattStatApplet(None, "dzen", int(sys.argv[2]))
    else:
      tpbattstat = TPBattStatApplet(None, "dzen")
    tpbattstat.startUpdate()
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

