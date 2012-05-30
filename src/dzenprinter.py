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
import inspect

IMAGE_HEIGHT = 36
IMAGE_WIDTH = 36
IMAGE_DIR = (
  '/usr/share/pixmaps/tpbattstat-applet/xpm' + 
  '/' + str(IMAGE_WIDTH) + 'x' + str(IMAGE_HEIGHT)
  )

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
      img = img + "/idle"

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
      return self.getImageMarkup(self.selectImage(installed, state, percent))
    else:
      return ''
  def getBattImageMarkup(self, batt_id):
    if self.prefs.display_icons and not self.prefs.display_only_one_icon:
      return self.getImageMarkup(self.selectImageByBattId(batt_id))
    else:
      return ''
  def getImageMarkup(self, img):
    return (""
      + "^p(;-8)"
      + "^i(" + img + ")"
      + "^p(;8)"
      )
  def getBattPercentMarkup(self, batt_id):
    battInfo = self.battStatus.getBattInfo(batt_id)
    if not battInfo.isInstalled():
      return 'X'
    percent = battInfo.remaining_percent

    if percent == '100':
      percent = '@@'
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
  def getPowerMarkup(self):
    return self.battStatus.getPowerDisplay()
  def getTopLength(self):
    bat0 = self.battStatus.getBattInfo(0).remaining_percent
    bat1 = self.battStatus.getBattInfo(1).remaining_percent
    return len(bat0) + len(bat1) + 1
  def raiseMarkup(self, markup):
    return "^p(;-10)" + markup + "^p(;10)"
  def lowerMarkup(self, markup):
    return "^p(;6)" + markup + "^p(;-6)"
  def twoTextRows(self, top, bot):
    if len(bot) == 0:
      return top
    for i in range(0, 6-self.getTopLength()):
      top = top + ' '
    top = self.raiseMarkup(top)
    bot = self.lowerMarkup(bot)
    return (''
     + '^ib(1)'
     + '^p(_LOCK_X)'
     + bot
     + '^p(_UNLOCK_X)'
     + top
     + '^ib(0)'
     )
  def wrapClick(self, btn, cmd, markup):
    return "^ca(" + btn + "," + cmd + ")" + markup + "^ca()"
  def getLeftClickCmd(self):
    exe=inspect.stack()[-1][1]
    return exe + " " + "--prefs"
  def getDzenMarkup(self):
    self.counter = self.counter + 1
    
    return self.wrapClick("1", self.getLeftClickCmd(), ""
      + self.getJointImage()
      + self.getBattImageMarkup(0)
      + self.twoTextRows(""
          + self.getBattPercentMarkup(0)
          + self.getSeparatorMarkup()
          + self.getBattPercentMarkup(1)
          ,
          self.getPowerMarkup()
        )
      + self.getBattImageMarkup(1)
      )

