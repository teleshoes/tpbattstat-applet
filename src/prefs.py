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

import sys
import re
from subprocess import Popen, PIPE
import gconf

SCHEMA_DIR = '/schemas/apps/tpbattstat_applet/prefs'

def enum(*sequential, **named):
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

State = enum('CHARGING', 'DISCHARGING', 'IDLE')
DischargeStrategy = enum('SYSTEM', 'LEAPFROG', 'CHASING')
ChargeStrategy = enum('SYSTEM', 'LEAPFROG', 'CHASING', 'BRACKETS')

class Prefs():
  def __init__(self, applet):
    self.client = gconf.client_get_default()
    self.gconf_root_key = applet.get_preferences_key()
    if self.gconf_root_key == None:
      self.gconf_root_key = '/apps/tpbattstat_applet/prefs'
      for schema in self.getAllKeysInSchema(SCHEMA_DIR):
        self.applySchema(schema)
    else:
      applet.add_preferences(SCHEMA_DIR)
  def update(self):
    self.delay = self.gconfGetInt(
        'delay', 1000)
    self.discharge_strategy = self.gconfGetDischargeStrategy()
    self.discharge_leapfrog_threshold = self.gconfGetInt(
        'discharge_leapfrog_threshold', 5)
    self.charge_strategy = self.gconfGetChargeStrategy()
    self.charge_leapfrog_threshold = self.gconfGetInt(
        'charge_leapfrog_threshold', 10)
    self.charge_brackets_pref_battery = self.gconfGetInt(
        'charge_brackets_pref_battery', 0)
    self.charge_brackets = self.gconfGetIntList(
        'charge_brackets', [10,20,80,90,95,100])
    self.display_power_avg = self.gconfGetBool(
        'display_power_avg', True)
    self.display_colored_text = self.gconfGetBool(
        'display_colored_text', True)
    self.display_icons = self.gconfGetBool(
        'display_icons', True)
    self.display_only_one_icon = self.gconfGetBool(
        'display_only_one_icon', False)
    self.display_blinking_indicator = self.gconfGetBool(
        'display_blinking_indicator', False)
  def getAllKeysInSchema(self, keydir):
    try:
      p = Popen(['gconftool', '--recursive-list', keydir], stdout=PIPE)
      (stdout, _) = p.communicate()
      schemas = []
      for schema in re.findall('[a-zA-Z0-9_]+ = Schema ', stdout):
        m = re.match('(.*) = Schema ', schema)
        schema = m.group(1)
        schemas.append(schema)
      return schemas
    except:
      msg = 'Could not list keys in ' + keydir
      print >> sys.stderr, msg
      return -1      
  def applySchema(self, key):
    try:
      schemaname = SCHEMA_DIR + '/' + key
      keyname = self.gconf_root_key + '/' + key
      p = Popen(['gconftool', '--apply-schema', schemaname, keyname])
      p.wait()
    except:
      msg = 'Could not apply schema for key ' + key
      print >> sys.stderr, msg
      return -1
  def gconfGetInt(self, key, default):
    val = self.client.get_int(self.gconf_root_key + '/' + key)
    if val == None:
      return default
    else:
      return val
  def gconfGetStr(self, key, default):
    val = self.client.get_string(self.gconf_root_key + '/' + key)
    if val == None:
      return default
    else:
      return val
  def gconfGetBool(self, key, default):
    val = self.client.get_bool(self.gconf_root_key + '/' + key)
    if val == None:
      return default
    else:
      return val
  def gconfGetIntList(self, key, default):
    val = self.client.get_list(self.gconf_root_key + '/' + key, 'int')
    if val == None or val == []:
      return default
    else:
      return val
  def gconfGetChargeStrategy(self):
    strat = self.gconfGetStr('charge_strategy', 'brackets').upper()
    if strat == 'SYSTEM':
      return ChargeStrategy.SYSTEM
    elif strat == 'LEAPFROG':
      return ChargeStrategy.LEAPFROG
    elif strat == 'CHASING':
      return ChargeStrategy.CHASING
    elif strat == 'BRACKETS':
      return ChargeStrategy.BRACKETS
    else:
      return None
  def gconfGetDischargeStrategy(self):
    strat = self.gconfGetStr('discharge_strategy', 'leapfrog').upper()
    if strat == 'SYSTEM':
      return DischargeStrategy.SYSTEM
    elif strat == 'LEAPFROG':
      return DischargeStrategy.LEAPFROG
    elif strat == 'CHASING':
      return DischargeStrategy.CHASING
    else:
      return None

