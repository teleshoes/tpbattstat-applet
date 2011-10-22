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

from battstatus import State
from gconfgui import GconfGui
from prefs import SCHEMA_DIR
import gtk
import gtk.gdk
import gnomeapplet

IMAGE_DIR = '/usr/share/pixmaps/tpbattstat-applet/svg'
IMAGE_HEIGHT = 24
IMAGE_WIDTH = 24

class Gui():
  def __init__(self, applet, prefs, battStatus):
    self.applet = applet
    self.prefs = prefs
    self.battStatus = battStatus
    self.label = gtk.Label("<?>")
    self.batt0img = gtk.Image()
    self.batt1img = gtk.Image()
    self.counter = 0
    self.initPixbufs()
    
    self.container = gtk.HBox()
    self.box = None
    self.resetLayout()
    self.create_menu()

    self.gconfGui = None
    self.applet.connect("change-orient", self.resetLayout)
  def getGtkWidget(self):
    return self.container
  def resetLayout(self):
    if self.box != None:
      self.container.remove(self.box)
    orient = self.applet.get_orient()

    if self.isVertical():
      self.box = gtk.VBox()
    else:
      self.box = gtk.HBox()

    self.box.add(self.batt0img)
    self.box.add(self.label)
    self.box.add(self.batt1img)
    
    self.container.add(self.box)
    self.container.show_all()
  def create_menu(self):
    xml="""<popup name="button3">
      <menuitem name="Preferences" verb="Preferences" label="_Preferences"
        pixtype="stock" pixname="gtk-preferences"/>
      <menuitem name="Statistics" verb="Statistics" label="_Statistics"/>
      <menuitem name="About" verb="About" label="_About"
        pixtype="stock" pixname="gtk-about"/>
      </popup>"""
    verbs = [("Preferences", self.showPreferencesDialog),
             ("Statistics", self.showStatisticsDialog),
             ("About", self.showAboutDialog)]
    self.applet.setup_menu(xml, verbs, None)

  def initPixbufs(self):
    self.none = self.newPixbuf('none.svg')
    self.idle = []
    self.charging = []
    self.discharging = []
    for i in [0,10,20,30,40,50,60,70,80,90,100]:
      img = str(i) + '.svg'
      self.idle.append(self.newPixbuf('idle/' + img))
      self.charging.append(self.newPixbuf('charging/' + img))
      self.discharging.append(self.newPixbuf('discharging/' + img))
  def newPixbuf(self, filename):
    return gtk.gdk.pixbuf_new_from_file_at_size(
      IMAGE_DIR + '/' + filename, IMAGE_WIDTH, IMAGE_HEIGHT)
  def selectPixbufByBattId(self, batt_id):
    battInfo = self.battStatus.getBattInfo(batt_id)
    return self.selectPixbuf(battInfo.isInstalled(), battInfo.state,
      int(battInfo.remaining_percent))
  def selectPixbuf(self, installed, state, percent):
    if not installed:
      return self.none

    if state == State.CHARGING:
      imgs = self.charging
    elif state == State.DISCHARGING:
      imgs = self.discharging
    else:
      imgs = self.idle
    i = percent / 10
    return imgs[i]
  def updateImages(self):
    if self.prefs.display_icons:
      if self.prefs.display_only_one_icon:
        installed = self.battStatus.isEitherInstalled()
        percent = self.battStatus.getTotalRemainingPercent()
        if self.battStatus.isEitherCharging():
          state = State.CHARGING
        elif self.battStatus.isEitherDischarging():
          state = State.DISCHARGING
        else:
          state = State.IDLE
        self.batt0img.set_from_pixbuf(
          self.selectPixbuf(installed, state, percent))
        self.batt0img.set_child_visible(True)
        self.batt1img.set_child_visible(False)
      else:
        self.batt0img.set_from_pixbuf(self.selectPixbufByBattId(0))
        self.batt1img.set_from_pixbuf(self.selectPixbufByBattId(1))
        self.batt0img.set_child_visible(True)
        self.batt1img.set_child_visible(True)
    else:
      self.batt0img.set_child_visible(False)
      self.batt1img.set_child_visible(False)

  def getBattMarkup(self, batt_id):
    battInfo = self.battStatus.getBattInfo(batt_id)
    if not battInfo.isInstalled():
      return '<span size="small">X</span>'
    percent = battInfo.remaining_percent

    if percent == '100':
      size = ' size="xx-small" '
    else:
      size = ' size="small" '

    if not self.prefs.display_colored_text or battInfo.state == State.IDLE:
      color = ''
    elif battInfo.state == State.CHARGING:
      color = ' foreground="#60FF60" '
    elif battInfo.state == State.DISCHARGING:
      color = ' foreground="#FF6060" '

    return '<b><span' + size + color + '>' + percent + '</span></b>'
  def getSeparatorMarkup(self):
    if self.prefs.display_blinking_indicator and self.counter % 2 == 0:
      color = ' foreground="blue" '
    else:
      color = ''

    sep = '<span size="x-small"' + color + '>|</span>'
    if self.isVertical():
      return sep + '\n'
    else:
      return sep
  def isVertical(self):
    orient = self.applet.get_orient()
    return not (orient == gnomeapplet.ORIENT_UP or
                orient == gnomeapplet.ORIENT_DOWN)
  def getPowerAvgMarkup(self):
    if not self.prefs.display_power_avg:
      return ''
    pow0 = int(self.battStatus.batt0.power_avg)
    pow1 = int(self.battStatus.batt1.power_avg)
    if pow0 != 0:
      powavg = pow0
    else:
      powavg = pow1
    powavgW = float(powavg / 100) / 10.0
    return '\n<span size="xx-small">' + str(powavgW) + 'W</span>'

  def updateLabel(self):
    self.label.set_markup(
      self.getBattMarkup(0) +
      self.getSeparatorMarkup() +
      self.getBattMarkup(1) +
      self.getPowerAvgMarkup())

  def update(self):
    self.counter = self.counter + 1
    self.updateImages()
    self.updateLabel()

  def showAboutDialog(self, *arguments, **keywords):
    dialog = gtk.Window(gtk.WINDOW_TOPLEVEL)
    dialog.set_title('About TPBattStatApplet')
    label = gtk.Label()
    label.set_markup("""
       <span size='x-large'>TPBattStatApplet v0.1</span>
       <span size='medium'>Copyright 2011 Elliot Wolk</span>
       
       <span size='medium'>ThinkPad Battery Status Applet for Gnome</span>

       TPBattStatApplet is free software: you can redistribute it and/or
       modify it under the terms of the GNU General Public License as
       published by the Free Software Foundation, either version 3 of the
       License, or (at your option) any later version.
       """)
    dialog.add(label)
    dialog.show_all()

  def ensurePreferencesDialog(self):
    if self.gconfGui != None and self.gconfGui.get_window() != None:
      return
    self.gconfGui = GconfGui(self.prefs.gconf_root_key, SCHEMA_DIR,[
      ('delay', 'delay', None, None, (0, None, 100, 1000), None),
      ('discharge_strategy', 'discharge_strategy', None, None, None,
        ['system', 'leapfrog', 'chasing']),
      ('discharge_leapfrog_threshold', 'discharge_leapfrog_threshold',
        None, None, (0, 100, 5, 20), None),
      ('charge_strategy', 'charge_strategy', None, None, None,
        ['system', 'leapfrog', 'chasing', 'brackets']),
      ('charge_leapfrog_threshold', 'charge_leapfrog_threshold',
        None, None, (0, 100, 5, 20), None),
      ('charge_brackets_pref_battery', 'charge_brackets_pref_battery',
        None, None, None, ['0','1']),
      ('charge_brackets', 'charge_brackets', None, None,
        (0, 100, 5, 20), None),
      ('display_power_avg', 'display_power_avg', None, None, None, None),
      ('display_colored_text', 'display_colored_text',
        None, None, None, None),
      ('display_icons', 'display_icons', None, None, None, None),
      ('display_only_one_icon', 'display_only_one_icon',
        None, None, None, None),
      ('display_blinking_indicator', 'display_blinking_indicator',
        None, None, None, None),
      ('led_patterns_charging', 'led_patterns',
        None, None, None, None),
      ('led_patterns_discharging', 'led_patterns',
        None, None, None, None),
      ('led_patterns_idle', 'led_patterns',
        None, None, None, None),
    ])
    self.prefsDialog = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.prefsDialog.set_title('TPBattStatApplet Preferences')
    self.prefsDialog.add(self.gconfGui)
  def getPreferencesDialog(self):
    self.ensurePreferencesDialog()
    return self.prefsDialog
  def showPreferencesDialog(self, *arguments, **keywords):
    self.getPreferencesDialog().show_all()

  def showStatisticsDialog(self, *arguments, **keywords):
    dialog = gtk.Window(gtk.WINDOW_TOPLEVEL)
    dialog.set_title('tp-smapi info')
    label = gtk.Label()
    label.set_markup("""
       <span size='x-large'>stats arent here yet</span>
       """)
    dialog.add(label)
    dialog.show_all()

