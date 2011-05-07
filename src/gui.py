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
import gtk
import gtk.gdk
import gnomeapplet

IMAGE_DIR = '/usr/share/pixmaps/tpbattstat-applet'
IMAGE_HEIGHT = 24
IMAGE_WIDTH = 24

class Gui():
  def __init__(self, prefs, battStatus):
    self.prefs = prefs
    self.battStatus = battStatus
    self.hbox = gtk.HBox()
    self.label = gtk.Label("<?>")
    self.batt0img = gtk.Image()
    self.batt1img = gtk.Image()
    self.hbox.add(self.batt0img)
    self.hbox.add(self.label)
    self.hbox.add(self.batt1img)
    self.counter = 0
    self.initPixbufs()
  def getGtkWidget(self):
    return self.hbox
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
        self.batt0img.set_visible(True)
        self.batt1img.set_visible(False)
      else:
        self.batt0img.set_from_pixbuf(self.selectPixbufByBattId(0))
        self.batt1img.set_from_pixbuf(self.selectPixbufByBattId(1))
        self.batt0img.set_visible(True)
        self.batt1img.set_visible(True)
    else:
      self.batt0img.set_visible(False)
      self.batt1img.set_visible(False)

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
    return '<span size="x-small"' + color + '>|</span>'
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

