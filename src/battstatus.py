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

from prefs import DischargeStrategy, ChargeStrategy, State
import sys
from subprocess import Popen, PIPE

SMAPI_BATTACCESS = '/usr/bin/smapi-battaccess'

def smapi_get(batt_id, prop):
  try:
    p = Popen([SMAPI_BATTACCESS, '-g', str(batt_id), prop], stdout=PIPE)
    (stdout, _) = p.communicate()
    return stdout
  except:
    msg = 'Could not get ' + prop + ' on bat ' + str(batt_id)
    print >> sys.stderr, msg
    return -1

def smapi_set(batt_id, prop, val):
  try:
    print >> sys.stderr, "setting BAT" + str(batt_id) + "/" + prop + " => " + val
    p = Popen([SMAPI_BATTACCESS, '-s', str(batt_id), prop, val])
    p.wait()
  except:
    msg = 'Could not set ' + prop + '=' + val + ' on bat ' + str(batt_id)
    print >> sys.stderr, msg

class BattStatus():
  def __init__(self, prefs):
    self.prefs = prefs
    self.batt0 = BattInfo(0)
    self.batt1 = BattInfo(1)
  def getBattInfo(self, batt_id):
    if batt_id == 0:
      return self.batt0
    elif batt_id == 1:
      return self.batt1
    else:
      return None
  def isACConnected(self):
    return self.ac_connected == '1'
  def update(self, prefs):
    self.ac_connected = smapi_get(-1, 'ac_connected')
    self.batt0.update(prefs)
    self.batt1.update(prefs)
    self.perhaps_inhibit_charge()
    self.perhaps_force_discharge()
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

  def ensure_charging(self, batt_id):
    previnhib0 = self.batt0.isChargeInhibited()
    previnhib1 = self.batt1.isChargeInhibited()
    charge0 = self.batt0.isCharging()
    charge1 = self.batt1.isCharging()
    if batt_id == 0 and (previnhib0 or (not charge0 and not previnhib1)):
      smapi_set(1, 'inhibit_charge_minutes', '1')
      smapi_set(0, 'inhibit_charge_minutes', '0')
    elif batt_id == 1 and (previnhib1 or (not charge1 and not previnhib0)):
      smapi_set(0, 'inhibit_charge_minutes', '1')
      smapi_set(1, 'inhibit_charge_minutes', '0')

  def perhaps_inhibit_charge(self):
    should_not_inhibit = (not self.isACConnected() or
      not self.batt0.isInstalled() or not self.batt1.isInstalled())
    charge0 = self.batt0.isCharging()
    charge1 = self.batt1.isCharging()
    per0 = int(self.batt0.remaining_percent)
    per1 = int(self.batt1.remaining_percent)
    strategy = self.prefs.charge_strategy
    if should_not_inhibit or strategy == ChargeStrategy.SYSTEM:
      if self.batt0.isChargeInhibited():
        smapi_set(0, 'inhibit_charge_minutes', '0')
      if self.batt1.isChargeInhibited():
        smapi_set(1, 'inhibit_charge_minutes', '0')
    elif strategy == ChargeStrategy.LEAPFROG:
      if per1 - per0 > self.prefs.charge_leapfrog_threshold:
        self.ensure_charging(1)
      elif per0 - per1 > self.prefs.charge_leapfrog_threshold:
        self.ensure_charging(0)
    elif strategy == ChargeStrategy.CHASING:
      if per1 > per0:
        ensure_charging(0)
      elif per0 > per1:
        ensure_charging(1)
    elif strategy == ChargeStrategy.BRACKETS:
      prefBat = self.prefs.charge_brackets_pref_battery
      unprefBat = 1 - prefBat
      percentPref = per0 if prefBat == 0 else per1
      percentUnpref = per0 if unprefBat == 0 else per1
      for bracket in self.prefs.charge_brackets:
        if percentPref < bracket:
          self.ensure_charging(prefBat)
          break
        elif percentUnpref < bracket:
          self.ensure_charging(unprefBat)
          break

  def perhaps_force_discharge(self):
    should_force = (not self.isACConnected() and
      self.batt0.isInstalled() and self.batt1.isInstalled())
    dis0 = self.batt0.isDischarging()
    dis1 = self.batt1.isDischarging()
    per0 = int(self.batt0.remaining_percent)
    per1 = int(self.batt1.remaining_percent)
    force0 = False
    force1 = False
    strategy = self.prefs.discharge_strategy
    if not should_force or strategy == DischargeStrategy.SYSTEM:
      force0 = False
      force1 = False
    elif strategy == DischargeStrategy.LEAPFROG:
      leapfrogThreshold = self.prefs.discharge_leapfrog_threshold
      if dis0:
        if per1 - per0 > leapfrogThreshold:
          force1 = True
        elif per0 > leapfrogThreshold:
          force0 = True
      elif dis1:
        if per0 - per1 > leapfrogThreshold:
          force0 = True
        elif per1 > leapfrogThreshold:
          force1 = True
      elif per0 > leapfrogThreshold and per0 > per1:
        force0 = True
      elif per1 > leapfrogThreshold and per1 > per0:
        force1 = True
    elif strategy == DischargeStrategy.CHASING:
      if per0 > per1:
        force0 = True
      elif per1 > per0:
        force1 = True

    prevforce0 = self.batt0.isForceDischarge()
    prevforce1 = self.batt1.isForceDischarge()

    if prevforce0 != force0 or prevforce1 != force1:
      smapi_set(0, 'force_discharge', '1' if force0 else '0')
      smapi_set(1, 'force_discharge', '1' if force1 else '0')


class BattInfo():
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
    self.installed = smapi_get(self.batt_id, 'installed')
    dischargeStrategy = prefs.charge_strategy
    if dischargeStrategy != DischargeStrategy.SYSTEM:
      self.force_discharge = smapi_get(self.batt_id, 'force_discharge')
    else:
      self.force_discharge = 0
    chargeStrategy = prefs.charge_strategy
    if chargeStrategy != ChargeStrategy.SYSTEM:
      self.inhibit_charge_minutes = smapi_get(
        self.batt_id, 'inhibit_charge_minutes')
    else:
      self.inhibit_charge_minutes = 0
    self.remaining_percent = smapi_get(self.batt_id, 'remaining_percent')
    self.power_avg = smapi_get(self.batt_id, 'power_avg')
    self.remaining_capacity = smapi_get(self.batt_id, 'remaining_capacity')
    self.last_full_capacity = smapi_get(self.batt_id, 'last_full_capacity')
    self.design_capacity = smapi_get(self.batt_id, 'design_capacity')
    state = smapi_get(self.batt_id, 'state')
    if state == '1':
      self.state = State.CHARGING
    elif state == '2':
      self.state = State.DISCHARGING
    elif state == '0':
      self.state = State.IDLE
    else:
      self.state = None
