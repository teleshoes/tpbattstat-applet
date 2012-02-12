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

from prefs import DischargeStrategy, ChargeStrategy
import sys
from subprocess import Popen

SMAPI_BATTACCESS = '/usr/bin/smapi-battaccess'

def smapi_set(batt_id, prop, val):
  try:
    print >> sys.stderr, "setting BAT" + str(batt_id) + "/" + prop + " => " + val
    p = Popen([SMAPI_BATTACCESS, '-s', str(batt_id), prop, val])
    p.wait()
  except:
    msg = 'Could not set ' + prop + '=' + val + ' on bat ' + str(batt_id)
    print >> sys.stderr, msg

class BattBalance():
  def __init__(self, prefs, battStatus):
    self.prefs = prefs
    self.battStatus = battStatus

  def update(self):
    self.perhaps_inhibit_charge()
    self.perhaps_force_discharge()

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
    ac = self.battStatus.ac
    b0 = self.battStatus.batt0
    b1 = self.battStatus.batt1
    should_not_inhibit = (
      not ac.isACConnected() or
      not b0.isInstalled() or
      not b1.isInstalled())
    charge0 = b0.isCharging()
    charge1 = b1.isCharging()
    per0 = int(b0.remaining_percent)
    per1 = int(b1.remaining_percent)
    strategy = self.prefs.charge_strategy
    if should_not_inhibit or strategy == ChargeStrategy.SYSTEM:
      if b0.isChargeInhibited():
        smapi_set(0, 'inhibit_charge_minutes', '0')
      if b1.isChargeInhibited():
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
    ac = self.battStatus.ac
    b0 = self.battStatus.batt0
    b1 = self.battStatus.batt1
    should_force = (
      not ac.isACConnected() and
      b0.isInstalled() and
      b1.isInstalled())
    dis0 = b0.isDischarging()
    dis1 = b1.isDischarging()
    per0 = int(b0.remaining_percent)
    per1 = int(b1.remaining_percent)
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

    prevforce0 = b0.isForceDischarge()
    prevforce1 = b1.isForceDischarge()

    if prevforce0 != force0 or prevforce1 != force1:
      smapi_set(0, 'force_discharge', '1' if force0 else '0')
      smapi_set(1, 'force_discharge', '1' if force1 else '0')

