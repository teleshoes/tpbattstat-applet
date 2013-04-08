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
from gui import Gui
from battstatus import BattStatus
from guimarkup import DzenPrinter
from actions import Actions
import sys
import gtk
import gobject

class TPBattStat():
  def __init__(self, mode, forceDelay=None):
    self.mode = mode
    self.forceDelay = forceDelay

    self.prefs = Prefs()
    self.battStatus = BattStatus(self.prefs)
    self.actions = Actions(self.prefs, self.battStatus)
    if self.mode == "gtk" or self.mode == "prefs":
      self.gui = Gui(self.prefs, self.battStatus)
    elif self.mode == "dzen":
      self.dzenprinter = DzenPrinter(self.prefs, self.battStatus)
      
  def getGui(self):
    return self.gui
  def startUpdate(self):
    self.curDelay = -1
    self.update()
  def update(self):
    try:
      self.prefs.update()
    except Exception as e:
      print 'ignoring prefs'
      print e.message
    if self.forceDelay != None:
      self.prefs['delay'] = self.forceDelay
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

    if self.prefs['delay'] != self.curDelay:
      self.curDelay = self.prefs['delay']
      if self.curDelay <= 0:
        self.curDelay = 1000
      gobject.timeout_add(self.curDelay, self.update)
      return False
    else:
      return True

def showAndExit(gtkElem):
  gtkElem.connect("destroy", gtk.main_quit) 
  gtkElem.show_all()
  gtk.main()
  sys.exit()

def prefsClickHandler(widget, event):
  if event.button == 1:
    prefsDialog = TPBattStat("prefs").getGui().showPreferencesDialog()

def main():
  if len(sys.argv) >= 2:
    arg = sys.argv[1]
  else:
    arg = None

  if arg == None or arg == "-h" or arg == "--help" or arg == "help":
    print "Usage:"
    print "  " + sys.argv[0] + " [-h | --help | help]"
    print "  " + sys.argv[0] + " [-w | --window | window]"
    print "  " + sys.argv[0] + " [-d | --dzen | dzen] [optional-delay-millis]"
    print "  " + sys.argv[0] + " [-p | --prefs | prefs]"

  elif arg == "-w" or arg == "--window" or arg == "window":
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title("TPBattStat")
    tpbattstat = TPBattStat("gtk")
    tpbattstat.startUpdate()
    window.add(tpbattstat.gui.getGtkWidget())
    window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
    window.connect("button_press_event", prefsClickHandler)
    showAndExit(window)
  elif arg == "-p" or arg == "--prefs" or arg == "prefs":
    prefsDialog = TPBattStat("prefs").getGui().getPreferencesDialog()
    showAndExit(prefsDialog)

  elif arg == "-d" or arg == "--dzen" or arg == "dzen":
    if len(sys.argv) == 3:
      tpbattstat = TPBattStat("dzen", int(sys.argv[2]))
    else:
      tpbattstat = TPBattStat("dzen")
    tpbattstat.startUpdate()
    gtk.main()
    sys.exit()

if __name__ == "__main__":
  sys.exit(main())

