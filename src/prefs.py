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

import os
import sys
import re
from subprocess import Popen, PIPE
import gconf

def enum(*sequential, **named):
  enums = dict(zip(sequential, sequential), **named)
  enums['valueOf'] = dict(enums)
  enums['names'] = sequential
  return type('Enum', (), enums)

State = enum('CHARGING', 'DISCHARGING', 'IDLE')
DischargeStrategy = enum('SYSTEM', 'LEAPFROG', 'CHASING')
ChargeStrategy = enum('SYSTEM', 'LEAPFROG', 'CHASING', 'BRACKETS')
Interface = enum('SMAPI', 'ACPI')
PowerUsage = enum('NOW', 'AVERAGE', 'OFF')

def getPrefs():
  return [
  "delay", ["int", 1000,
    "Delay in ms between updates", None],
  "interface", ["enum", "SMAPI",
    "Battery info interface (smapi/acpi)",
    Interface],

  "dischargeStrategy", ["enum", "LEAPFROG",
    "Strategy for selecting battery to discharge",
    DischargeStrategy],
  "dischargeLeapfrogThreshold", ["int", 5,
    "Threshold to justify switching currently discharging battery", None],
  "chargeStrategy", ["enum", "BRACKETS",
    "Strategy for selecting battery to charge",
    ChargeStrategy],
  "chargeLeapfrogThreshold", ["int", 10,
    "Threshold to justify switching currently charging battery", None],
  "chargeBrackets", ["list-int", [10, 20, 80, 90, 95, 100],
    "Brackets to ensure even charge in charge_strategy=brackets.", None],
  "chargeBracketsPrefBattery", ["int", 0,
    "Battery to charge when both batteries are in the same bracket", None],

  "displayPowerUsage", ["enum", "NOW",
    "Display power rate in watts, instantaneous or average over the last 60s",
    PowerUsage],
  "displayColoredText", ["bool", True,
    "Green/red for charging/discharging", None],
  "displayIcons", ["bool", True,
    "Show battery icon(s)", None],
  "displayOnlyOneIcon", ["bool", True,
    "Show one icon with the sum of remaining charge of both batteries", None],
  "displayBlinkingIndicator", ["bool", True,
    "Alternate separator color every time the display updates", None],
  "ledPatternsCharging", ["list-string", [],
    "Patterns for the battery LED when charging", None],
  "ledPatternsDischarging", ["list-string", [],
    "Patterns for the battery LED when charging", None],
  "ledPatternsIdle", ["list-string", [],
    "Patterns for the battery LED when idle", None]
  ]
 
class Prefs():
  def __init__(self):
    self.prefsDir = os.environ['HOME'] + '/' + '.config'
    self.prefsFile = self.prefsDir + '/' + 'tpbattstat.conf'

    prefsArr = getPrefs()
    self.prefs = dict(zip(prefsArr[0::2], prefsArr[1::2]))
    self.names = prefsArr[0::2]
    self.types = dict([(k, v[0]) for (k, v) in self.prefs.iteritems()])
    self.defaults = dict([(k, v[1]) for (k, v) in self.prefs.iteritems()])
    self.enums = dict([(k, v[3]) for (k, v) in self.prefs.iteritems()])
    self.descShort = dict([(k, v[2]) for (k, v) in self.prefs.iteritems()])
    self.descLong = getPrefsLongDescriptions()

    self.curPrefs = dict(self.defaults)
    self.lastMod = -1
  def __getitem__(self, pref):
    if pref not in self.curPrefs:
      raise Exception("Unknown preference requested: " + pref)
    return self.curPrefs[pref]
  def getDefaultPrefsFile(self):
    s = ''
    for key in self.names:
      s += key + " = " + str(self.defaults[key])
      s += ' #' + self.descShort[key] + "\n"
    return s
  def ensurePrefsFile(self):
    self.getDefaultPrefsFile()
    if not os.path.isdir(self.prefsDir):
      os.makedirs(self.prefsDir, 0755)
    if not os.path.isfile(self.prefsFile):
      file(self.prefsFile, 'w').write(self.getDefaultPrefsFile())
  def checkPrefsFileChanged(self):
    if not os.path.isfile(self.prefsFile):
      return True
    mod = os.path.getmtime(self.prefsFile)
    if self.lastMod != mod:
      self.lastMod = mod
      return True
    return False
  def readPrefsFile(self):
    self.ensurePrefsFile()
    d = dict()
    for line in file(self.prefsFile).readlines():
      line = line.partition('#')[0]
      line = line.strip()
      if len(line) > 0:
        keyVal = line.split('=', 1)
        if len(keyVal) != 2:
          raise Exception("Error parsing config line: " + line)
        key = keyVal[0].strip()
        val = keyVal[1].strip()
        if key not in self.prefs:
          raise Exception("Unknown pref: " + key)
        d[key] = self.readVal(key, self.types[key], val, self.enums[key])
    return d
  def writePrefsFile(self):
    s = ''
    for key in self.names:
      val = self.curPrefs[key]
      if val != self.defaults[key]:
        s += key + " = " + str(val) + "\n"
    file(self.prefsFile, 'w').write(s)
  def readVal(self, key, valType, valStr, enumVals):
    valStr = valStr.strip()
    if valType == 'int':
      try:
        return int(valStr)
      except ValueError:
        raise Exception("%s must be an integer: %s" % (key, valStr))
    elif valType == 'bool':
      if valStr.lower() == "true":
        return True
      elif valStr.lower() == "false":
        return False
      else:
        raise Exception("%s must be true/false: %s" % (key, valStr))
    elif valType == 'string':
      return valStr
    elif valType == 'enum':
      if enumVals == None:
        raise Exception("No enum defined for pref " + key)
      valStr = valStr.upper()
      if valStr.upper() not in enumVals.names:
        raise Exception("%s must be one of (%s): %s" %
          (key, str(enumVals.names), valStr))
      return enumVals.valueOf[valStr]
    elif valType[:5] == "list-":
      listType = valType[5:]
      if valStr[0] == '[' and valStr[-1] == ']':
        valStr = valStr[1:-1]
      else:
        raise Exception("%s must be a list (e.g.:[v, v]): %s'" % (key, valStr))
      valList = []
      if len(valStr) > 0:
        for val in valStr.split(','):
          val = val.strip()
          valList.append(self.readVal(key, listType, val, enumVals))
      return valList
  def update(self):
    if self.checkPrefsFileChanged():
      self.curPrefs.update(self.readPrefsFile())

def getPrefsLongDescriptions():
  ledDescription = """
  A list of led-pattern-strings to pass to led-batt.
  There are three lists of led-pattern-strings, one for
    charging, discharging, and idle.
  Patterns are chosen based on the current total remaining battery percent;
    The patterns divide up the percentage ranges,
      based on how many patterns there are.
    {the left-most pattern is always used at 0% and the right-most at 100%}
    e.g.: if there are four patterns: 0-24%, 25-49%, 50-74%, 75-100%
  
  led-batt accepts either a single keyword arg, or a list of commands.
  available keywords:
    green            orange       both
    slowblink-green  blink-green  fastblink-green
    slowblink-orange blink-orange fastblink-orange
    slowblink-both   blink-both   fastblink-both
    off
 
  available led commands:
    G : turn green light on
    g : turn green light off
    O : turn orange light on
    o : turn orange light off
    # : pause for # seconds {e.g.: 0.1 or 60 or 1.2}

  examples:
    1) [blink-orange, blink-both, blink-green]
       0% -  33% : blink orange light
      34% -  66% : blink both lights
      67% - 100% : blink green light
    2) [fastblink-orange, both, "o G 5 g O 5", green]
       0% -  24% : blink orange light quickly
      25% -  49% : show both lights steady
      50% -  74% : cycle between orange and green every 5 seconds
      75% - 100% : show green light steady
  """

  return {
    "interface": """
      Interface for obtaining battery information.
      Valid values include: "smapi", and "acpi"
      smapi:
        read values from /sys/devices/platform/smapi
      acpi:
        read values from /proc/acpi/battery
      NOTE: power_now only works in smapi
    """,
    "ledPatternsCharging": ledDescription,
    "ledPatternsDischarging": ledDescription,
    "ledPatternsIdle": ledDescription
  }
