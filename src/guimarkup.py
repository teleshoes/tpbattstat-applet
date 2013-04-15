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
import inspect
import re

IMAGE_DIR = '/usr/share/pixmaps/tpbattstat-applet/xpm'

CHARGING_COLOR = '#60FF60'
DISCHARGING_COLOR = '#FF6060'

class MarkupBuilder():
  def fg(self, color, markup): pass
  def appendImage(self, image): pass
  def appendLabel(self, text): pass
  def setClickCmd(self, clickCmd): pass
  def stripMarkup(self, text): pass
  def toString(self): pass

  def estimateLength(self, text):
    return len(self.stripMarkup(text))
  def pad(self, text, length):
    curLen = self.estimateLength(text)
    for i in range(0, length-curLen):
      text += ' '
    return text


class JsonMarkupBuilder(MarkupBuilder):
  def __init__(self):
    self.items = []
  def fg(self, color, markup):
    return "<span foreground=\"" + color + "\">" + markup + "</span>"
  def appendImage(self, image):
    self.append("image", image)
  def appendLabel(self, text):
    self.append("label", text)
  def setClickCmd(self, clickCmd):
    self.append("click", clickCmd)
  def stripMarkup(self, m):
    return re.sub('<[^>]*>', '', m)
  def toString(self):
    return "{" + ', '.join(self.items) + "}"

  def append(self, name, value):
    if value:
      value = self.escapeMarkup(value)
      self.items.append("\"" + name + "\": \"" + value + "\"")
  def escapeMarkup(self, m):
    return m.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

class DzenMarkupBuilder(MarkupBuilder):
  def __init__(self):
    self.markup = ""
  def fg(self, color, markup):
    return "^fg(" + color + ")" + markup + "^fg()"
  def appendImage(self, image):
    if image:
      self.markup += "^p(;-8)" + "^i(" + image + ")" + "^p(;8)"
  def appendLabel(self, text):
    lines = text.split("\n")
    self.markup += self.getLinesMarkup(lines)
  def setClickCmd(self, clickCmd):
    self.markup = self.wrapClickMarkup(1, clickCmd, self.markup)
  def toString(self):
    return self.markup
  def stripMarkup(self, m):
    return re.sub('\\^[a-z]+\\(.*?\\)', '', m)

  def getLinesMarkup(self, lines):
    if len(lines) == 0:
      return ''
    elif len(lines) == 1:
      return lines[0]
    else:
      top = lines[0]
      bot = ' '.join(lines[1:])
      return self.twoTextRows(top, bot)
  def wrapClickMarkup(self, btn, cmd, markup):
    return "^ca(" + str(btn) + "," + cmd + ")" + markup + "^ca()"
  def raiseMarkup(self, markup):
    return "^p(;-10)" + markup + "^p(;10)"
  def lowerMarkup(self, markup):
    return "^p(;6)" + markup + "^p(;-6)"
  def twoTextRows(self, top, bot):
    if len(bot) == 0:
      return top
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


class GuiMarkupPrinter():
  def __init__(self, prefs, battStatus):
    self.prefs = prefs
    self.battStatus = battStatus
    self.counter = 0
  def selectImageByBattId(self, batt_id):
    battInfo = self.battStatus.getBattInfo(batt_id)
    return self.selectImage(battInfo.isInstalled(), battInfo.state,
      int(float(battInfo.remaining_percent)))
  def imageDir(self):
    return IMAGE_DIR + '/' + self.prefs['iconSize']
  def selectImage(self, installed, state, percent):
    if not installed:
      return self.imageDir() + "/none.xpm"

    img = self.imageDir()
    if state == State.CHARGING:
      img = img + "/charging"
    elif state == State.DISCHARGING:
      img = img + "/discharging"
    else:
      img = img + "/idle"

    img = img + "/" + str(percent / 10 * 10) + ".xpm"
    return img
  def getJointImage(self):
    if self.prefs['displayIcons'] and self.prefs['displayOnlyOneIcon']:
      installed = self.battStatus.isEitherInstalled()
      percent = self.battStatus.getTotalRemainingPercent()
      if self.battStatus.isEitherCharging():
        state = State.CHARGING
      elif self.battStatus.isEitherDischarging():
        state = State.DISCHARGING
      else:
        state = State.IDLE
      return self.selectImage(installed, state, percent)
    else:
      return None
  def getBattImage(self, batt_id):
    if self.prefs['displayIcons'] and not self.prefs['displayOnlyOneIcon']:
      return self.selectImageByBattId(batt_id)
    else:
      return None
  def getBattPercentMarkup(self, batt_id):
    battInfo = self.battStatus.getBattInfo(batt_id)
    if not battInfo.isInstalled():
      return 'X'
    percent = battInfo.remaining_percent

    if percent == '100':
      percent = '@@'

    if not self.prefs['displayColoredText'] or battInfo.state == State.IDLE:
      return percent
    elif battInfo.state == State.CHARGING:
      return self.markupBuilder.fg(CHARGING_COLOR, percent)
    elif battInfo.state == State.DISCHARGING:
      return self.markupBuilder.fg(DISCHARGING_COLOR, percent)
  def getSeparatorMarkup(self):
    sep = "|"
    if self.prefs['displayBlinkingIndicator'] and self.counter % 2 == 0:
      return self.markupBuilder.fg("blue",  sep)
    else:
      return sep
  def getPowerMarkup(self):
    return self.battStatus.getPowerDisplay()
  def getLeftClickCmd(self):
    exe=inspect.stack()[-1][1]
    return exe + " " + "--prefs"
  def getBattLabelMarkup(self):
    return (''
          + self.getBattPercentMarkup(0)
          + self.getSeparatorMarkup()
          + self.getBattPercentMarkup(1)
          )
  def getMarkupJson(self):
    self.markupBuilder = JsonMarkupBuilder()
    return self.getGuiMarkup()
  def getMarkupDzen(self):
    self.markupBuilder = DzenMarkupBuilder()
    return self.getGuiMarkup()
  def getGuiMarkup(self):
    self.counter = self.counter + 1

    self.markupBuilder.appendImage(self.getJointImage())
    self.markupBuilder.appendImage(self.getBattImage(0))
    self.markupBuilder.appendLabel(''
          + self.markupBuilder.pad(self.getBattLabelMarkup(), 6)
          + "\n"
          + self.markupBuilder.pad(self.getPowerMarkup(), 6)
          )
    self.markupBuilder.appendImage(self.getBattImage(1))
    self.markupBuilder.setClickCmd(self.getLeftClickCmd())
    return self.markupBuilder.toString()
