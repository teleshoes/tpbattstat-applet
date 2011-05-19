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
from prefs import SCHEMA_DIR

IMAGE_DIR = '/usr/share/pixmaps/tpbattstat-applet/xpm'
IMAGE_HEIGHT = 24
IMAGE_WIDTH = 24

class DzenPrinter():
  def __init__(self, prefs, battStatus):
    self.prefs = prefs
    self.battStatus = battStatus
    self.counter = 0
  def selectImageByBattId(self, batt_id):
    battInfo = self.battStatus.getBattInfo(batt_id)
    return self.selectImage(battInfo.isInstalled(), battInfo.state,
      int(battInfo.remaining_percent))
  def selectImage(self, installed, state, percent):
    if not installed:
      return IMAGE_DIR + "/none.xpm"

    img = IMAGE_DIR
    if state == State.CHARGING:
      img = img + "/charging"
    elif state == State.DISCHARGING:
      img = img + "/discharging"
    else:
      imgs = img + "/idle"

    img = img + "/" + str(percent / 10 * 10) + ".xpm"
    return img
  def getJointImage(self):
    if self.prefs.display_icons and self.prefs.display_only_one_icon:
      installed = self.battStatus.isEitherInstalled()
      percent = self.battStatus.getTotalRemainingPercent()
      if self.battStatus.isEitherCharging():
        state = State.CHARGING
      elif self.battStatus.isEitherDischarging():
        state = State.DISCHARGING
      else:
        state = State.IDLE
      return "^i(" + self.selectImage(installed, state, percent) + ")"
    else:
      return ''
  def getBattImageMarkup(self, batt_id):
    if self.prefs.display_icons and not self.prefs.display_only_one_icon:
        return "^i(" + self.selectImageByBattId(batt_id) + ")"
    else:
      return ''
  def getBattPercentMarkup(self, batt_id):
    battInfo = self.battStatus.getBattInfo(batt_id)
    if not battInfo.isInstalled():
      return 'X'
    percent = battInfo.remaining_percent

    if not self.prefs.display_colored_text or battInfo.state == State.IDLE:
      color = ''
    elif battInfo.state == State.CHARGING:
      color = '#60FF60'
    elif battInfo.state == State.DISCHARGING:
      color = '#FF6060'

    return '^fg(' + color + ')' + percent + '^fg()'
  def getSeparatorMarkup(self):
    if self.prefs.display_blinking_indicator and self.counter % 2 == 0:
      color = 'blue'
    else:
      color = ''

    return '^fg(' + color + ')|^fg()'
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
    return str(powavgW) + 'W'

  def getDzenMarkup(self):
    self.counter = self.counter + 1

    return (""
      + self.getJointImage()
      + self.getBattImageMarkup(0)
      + self.getBattPercentMarkup(0)
      + self.getSeparatorMarkup()
      + self.getBattPercentMarkup(1)
      + self.getPowerAvgMarkup()
      + self.getBattImageMarkup(1)
      )

