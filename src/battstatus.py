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

from prefs import State, ChargeStrategy, DischargeStrategy
from battbalance import BattBalance
import sys
import re
import os
from subprocess import Popen, PIPE

SMAPI_BATTACCESS = '/usr/bin/smapi-battaccess'

class BattStatus():
  def __init__(self, prefs):
    self.prefs = prefs
    self.battBalance = BattBalance(prefs, self)
    self.last_acpi = None
  def getBattInfo(self, batt_id):
    if batt_id == 0:
      return self.batt0
    elif batt_id == 1:
      return self.batt1
    else:
      return None
  def getPowerDisplay(self):
    disp = self.prefs.display_power_usage.lower()
    if disp == 'average':
      p0 = int(self.batt0.power_avg)
      p1 = int(self.batt1.power_avg)
    elif disp == 'now':
      p0 = int(self.batt0.power_now)
      p1 = int(self.batt1.power_now)
    else:
      return ''

    if p0 != 0:
      p = p0
    else:
      p = p1
    return "%3.1fW" % (p/1000.0)
  def update(self, prefs):
    if self.last_acpi != self.prefs.use_acpi:
      if self.prefs.use_acpi:
        self.last_acpi = True
        self.ac = ACInfoAcpi()
        self.batt0 = BattInfoAcpi(0)
        self.batt1 = BattInfoAcpi(1)
      else:
        self.last_acpi = False
        self.ac = ACInfoSmapi()
        self.batt0 = BattInfoSmapi(0)
        self.batt1 = BattInfoSmapi(1)

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


class ACInfoAcpi():
  def isACConnected(self):
    return self.ac_connected == '1'
  def acpiAcPath(self):
    return '/proc/acpi/ac_adapter/AC/state'
  def update(self, prefs):
    if os.path.isfile(self.acpiAcPath()):
      s = file(self.acpiAcPath()).read()
      if 'on-line' in s:
        self.ac_connected = '1'
      else:
        self.ac_connected = '0'
    else:
        self.ac_connected = '0'

class BattInfoAcpi():
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
  def acpiDir(self):
    return "/proc/acpi/battery/BAT" + str(self.batt_id)
  def acpiStatePath(self):
    return self.acpiDir() + '/state'
  def acpiInfoPath(self):
    return self.acpiDir() + '/info'
  def clear(self):
    self.installed = '0'
    self.remaining_percent = '0'
    self.power_avg = '0'
    self.power_now = '0'
    self.remaining_capacity = '0'
    self.last_full_capacity = '0'
    self.design_capacity = '0'
    self.state = None
    
    self.force_discharge = '0'
    self.inhibit_charge_minutes = '0'
  def parseAcpi(self, fileContent):
    d = dict()
    keyValRe = re.compile('([a-zA-Z0-9 ]+):\s*([a-zA-Z0-9 ]+)')
    for line in fileContent.splitlines():
      m = keyValRe.match(line)
      if m != None:
        d[m.group(1)] = m.group(2)
    return d
  def getValueAndUnit(self, s):
    m = re.compile('(\d+)\s*([a-zA-Z]*)').match(s)
    if m == None:
      return None
    else:
      return [int(m.group(1)), m.group(2)]
  def extractCurrent(self, info, voltMv):
    valUnit = self.getValueAndUnit(info)
    if valUnit == None:
      return None
    (val, unit) = valUnit

    if unit == 'mAh' or unit == 'mA':
      return val
    elif unit == 'mWh' or unit == 'mW':
      return val / (voltMv / 1000.0)
    else:
      return None
  def update(self, prefs):
    self.clear()
    statePresent = os.path.isfile(self.acpiStatePath())
    infoPresent = os.path.isfile(self.acpiInfoPath())
    if statePresent and infoPresent:
      self.installed = '1'
    else:
      self.installed = '0'

    if self.installed == '1':
      atts = dict()
      atts.update(self.parseAcpi(file(self.acpiStatePath()).read()))
      atts.update(self.parseAcpi(file(self.acpiInfoPath()).read()))
      print atts['present rate']

      try:
        voltValUnit = self.getValueAndUnit(atts['present voltage'])
        if voltValUnit == None or voltValUnit[1] != 'mV':
          return
        voltMv = voltValUnit[0]

        remMah = self.extractCurrent(atts['remaining capacity'], voltMv)
        lastMah = self.extractCurrent(atts['last full capacity'], voltMv)
        designMah = self.extractCurrent(atts['design capacity'], voltMv)
        rateMa = self.extractCurrent(atts['present rate'], voltMv)
        charge = atts['charging state']

        if (False
          or remMah < 0
          or lastMah <= 0
          or rateMa < 0
          or voltMv < 0
          ): return

        if charge == 'charging':
          self.state = State.CHARGING
        elif charge == 'discharging':
          self.state = State.DISCHARGING
        else:
          self.state = State.IDLE

        self.remaining_capacity = str(remMah)
        self.last_full_capacity = str(lastMah)
        self.design_capacity = str(designMah)
        self.remaining_percent = str(int(float(remMah) / float(lastMah) * 100.0))
        power = int(voltMv/1000.0 * rateMa) #mW
        if self.state == State.DISCHARGING and power > 0:
          self.power_avg = str(0 - power)
        else:
          self.power_avg = str(power)
        self.power_now = str(-1) #unsupported in acpi
      except:
        self.clear()

