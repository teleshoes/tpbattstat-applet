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
from actions import Actions
import sys
import gtk
import gobject
try:
  import gnomeapplet
  gnomeappletOk = True
except ImportError:
  gnomeappletOk = False 
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
    self.actions = Actions(self.prefs, self.battStatus)
    if self.mode == "gtk":
      self.gui = Gui(self.applet, self.prefs, self.battStatus)
      if gnomeappletOk:
        self.applet.add_preferences(SCHEMA_DIR)
        self.applet.add(self.gui.getGtkWidget())
        self.applet.set_background_widget(self.applet)
        self.applet.show_all()
    elif self.mode == "dzen":
      self.dzenprinter = DzenPrinter(self.prefs, self.battStatus)
      
  def getGui(self):
    return self.gui
  def startUpdate(self):
    self.curDelay = -1
    self.update()
  def update(self):
    self.prefs.update()
    if self.forceDelay != None:
      self.prefs.delay = self.forceDelay
    self.battStatus.update(self.prefs)

    self.actions.performActions()
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
  TPBattStatApplet(applet).startUpdate()
  return True

def showAndExit(gtkElem):
  gtkElem.connect("destroy", gtk.main_quit) 
  gtkElem.show_all()
  gtk.main()
  sys.exit()

def main():
  if len(sys.argv) >= 2:
    arg = sys.argv[1]
  else:
    arg = None

  if arg == "-h" or arg == "--help" or arg == "help":
    print "Usage:"
    print "  " + sys.argv[0] + " [-h | --help | help]"
    print "  " + sys.argv[0] + " [-w | --window | window]"
    print "  " + sys.argv[0] + " [-d | --dzen | dzen] [optional-delay-millis]"
    print "  " + sys.argv[0] + " [-p | --prefs | prefs]"

  elif arg == "-w" or arg == "--window" or arg == "window":
    if gnomeappletOk:
      applet = gnomeapplet.Applet()
    else:
      applet = None
    TPBattStatAppletFactory(applet, None)
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title("TPBattStatApplet")
    if gnomeappletOk:
      applet.reparent(window)
    showAndExit(window)

  elif arg == "-p" or arg == "--prefs" or arg == "prefs":
    if gnomeappletOk:
      applet = gnomeapplet.Applet()
    else:
      applet = None
    prefsDialog = TPBattStatApplet(applet).getGui().getPreferencesDialog()
    showAndExit(prefsDialog)

  elif arg == "-d" or arg == "--dzen" or arg == "dzen":
    if len(sys.argv) == 3:
      tpbattstat = TPBattStatApplet(None, "dzen", int(sys.argv[2]))
    else:
      tpbattstat = TPBattStatApplet(None, "dzen")
    tpbattstat.startUpdate()
    gtk.main()
    sys.exit()

  elif gnomeappletOk:
    gnomeapplet.bonobo_factory(
      "OAFIID:TPBattStatApplet_Factory", 
      gnomeapplet.Applet.__gtype__, 
      "ThinkPad Battery Status Applet",
      "0",
      TPBattStatAppletFactory)

if __name__ == "__main__":
  sys.exit(main())

