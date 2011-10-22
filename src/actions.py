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
from subprocess import Popen

LED_BATT_EXEC = '/usr/local/sbin/led-batt'

class Actions():
  def __init__(self, prefs, battStatus):
    self.prefs = prefs
    self.battStatus = battStatus
    self.ledPattern = None
    self.nullFile = open('/dev/null', 'w')
  def performActions(self):
    self.updateLed()
  def updateLed(self):
    newLed = self.calculateLedPattern()
    if self.ledPattern != newLed:
      self.ledPattern = newLed
      if self.ledPattern != []:

        Popen([LED_BATT_EXEC] + self.ledPattern, stdout=self.nullFile)
  def calculateLedPattern(self):
    if self.battStatus.isEitherCharging():
      patterns = self.prefs.ledPatternsCharging
    elif self.battStatus.isEitherDischarging():
      patterns = self.prefs.ledPatternsDischarging
    else:
      patterns = self.prefs.ledPatternsIdle
    if patterns == []:
      return []
    else:
      per = self.battStatus.getTotalRemainingPercent()
      index = int( (len(patterns)-1) * per / 100.0)
      pattern = patterns[index]
      return self.parsePattern(pattern)
  def parsePattern(self, pattern):
    return pattern.split(':')
