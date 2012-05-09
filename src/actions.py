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

from prefs import SCHEMA_DIR, State
from subprocess import Popen
import os
import re

LED_EXEC = '/usr/local/sbin/led'
LED_BATT_EXEC = '/usr/local/sbin/led-batt'
LED_DEV_DIR = '/sys/devices/platform/thinkpad_acpi/leds'
LED_GREEN_DEV = LED_DEV_DIR + '/tpacpi:green:batt/brightness'
LED_ORANGE_DEV = LED_DEV_DIR + '/tpacpi:orange:batt/brightness'

class Actions():
  def __init__(self, prefs, battStatus):
    self.prefs = prefs
    self.battStatus = battStatus
    self.ledPattern = None
  def performActions(self):
    self.updateLed()
  def updateLed(self):
    self.ledsOk = (
      os.path.isfile(LED_EXEC) and
      os.path.isfile(LED_BATT_EXEC) and
      os.path.isfile(LED_GREEN_DEV) and
      os.path.isfile(LED_ORANGE_DEV)
    )

    if self.ledsOk:
      newLed = self.calculateLedPattern()
      if self.ledPattern != newLed:
        self.ledPattern = newLed
        print "using led pattern: " + str(self.ledPattern)
        nullFile = open('/dev/null', 'w')
        if self.ledPattern != []:
          Popen([LED_BATT_EXEC] + self.ledPattern, stdout=nullFile)
        nullFile.close()
  def calculateLedPattern(self):
    if self.battStatus.isEitherCharging():
      patterns = self.prefs.ledPatternsCharging
    elif self.battStatus.isEitherDischarging():
      patterns = self.prefs.ledPatternsDischarging
    else:
      patterns = self.prefs.ledPatternsIdle
    length = len(patterns)
    pattern = ''
    if length > 0:
      per = self.battStatus.getTotalRemainingPercent()
      index = int(length * per / 100.0)
      if index >= length:
        index = length - 1
      if index < 0:
        index = 0
      pattern = patterns[index]
    return self.parsePattern(pattern)
  def parsePattern(self, pattern):
    return filter(None, re.split(' +', pattern))
