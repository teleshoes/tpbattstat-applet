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

from prefs import State
from battbalance import BattBalance
import sys
import re
import os
from subprocess import Popen, PIPE

SMAPI_BATTACCESS = '/usr/bin/smapi-battaccess'

def extractInt(s):
  try:
    return int(re.compile('\d+').match(s).group())
  except:
    return -1

class BattStatus():
  def __init__(self, prefs):
    self.prefs = prefs
    self.ac = ACInfoSmapi()
    self.batt0 = BattInfoSmapi(0)
    self.batt1 = BattInfoSmapi(1)
    self.battBalance = BattBalance(prefs, self)
  def getBattInfo(self, batt_id):
    if batt_id == 0:
      return self.batt0
    elif batt_id == 1:
      return self.batt1
    else:
      return None
  def update(self, prefs):
    self.ac.update(prefs)
    self.batt0.update(prefs)
    self.batt1.update(prefs)
    self.battBalance.update()
  def isEitherInstalled(self):
    return self.batt0.isInstalled() or self.batt1.isInstalled()
  def isEitherCharging(self):
    return self.batt0.isCharging() or self.batt1.isCharging()
  def isEitherDischarging(self):
    return self.batt0.isDischarging() or self.batt1.isDischarging()
  def getTotalRemainingPercent(self):
    rem_cap = 0
    max_cap = 0
    if self.batt0.isInstalled():
      rem_cap = rem_cap + int(self.batt0.remaining_capacity)
      max_cap = max_cap + int(self.batt0.last_full_capacity)
    if self.batt1.isInstalled():
      rem_cap = rem_cap + int(self.batt1.remaining_capacity)
      max_cap = max_cap + int(self.batt1.last_full_capacity)
    if max_cap == 0:
      return 0
    return int(100 * (float(rem_cap) / float(max_cap)))

class InfoSmapi():
  def smapi_get(self, batt_id, prop):
    try:
      p = Popen([SMAPI_BATTACCESS, '-g', str(batt_id), prop], stdout=PIPE)
      (stdout, _) = p.communicate()
      return stdout
    except:
      msg = 'Could not get ' + prop + ' on bat ' + str(batt_id)
      print >> sys.stderr, msg
      return -1

class ACInfoSmapi(InfoSmapi):
  def isACConnected(self):
    return self.ac_connected == '1'
  def update(self, prefs):
    self.ac_connected = self.smapi_get(-1, 'ac_connected')
    
class BattInfoSmapi(InfoSmapi):
  def __init__(self, batt_id):
    self.batt_id = batt_id
  def isInstalled(self):
    return self.installed == '1'
  def isCharging(self):
    return self.state == State.CHARGING
  def isDischarging(self):
    return self.state == State.DISCHARGING
  def isChargeInhibited(self):
    return int(self.inhibit_charge_minutes) > 0
  def isForceDischarge(self):
    return self.force_discharge == '1'
  def update(self, prefs):
    self.installed = self.smapi_get(self.batt_id, 'installed')
    dischargeStrategy = prefs.discharge_strategy
    if dischargeStrategy != DischargeStrategy.SYSTEM:
      self.force_discharge = self.smapi_get(self.batt_id, 'force_discharge')
    else:
      self.force_discharge = 0
    chargeStrategy = prefs.charge_strategy
    if chargeStrategy != ChargeStrategy.SYSTEM:
      self.inhibit_charge_minutes = self.smapi_get(
        self.batt_id, 'inhibit_charge_minutes')
    else:
      self.inhibit_charge_minutes = 0
    self.remaining_percent = self.smapi_get(self.batt_id, 'remaining_percent')
    self.power_avg = self.smapi_get(self.batt_id, 'power_avg')
    self.power_now = self.smapi_get(self.batt_id, 'power_now')
    self.remaining_capacity = self.smapi_get(self.batt_id, 'remaining_capacity')
    self.last_full_capacity = self.smapi_get(self.batt_id, 'last_full_capacity')
    self.design_capacity = self.smapi_get(self.batt_id, 'design_capacity')
    state = self.smapi_get(self.batt_id, 'state')
    if state == '1':
      self.state = State.CHARGING
    elif state == '2':
      self.state = State.DISCHARGING
    elif state == '0':
      self.state = State.IDLE
    else:
      self.state = None

