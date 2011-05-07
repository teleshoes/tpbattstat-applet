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

import gconf

SCHEMA_DIR = '/schemas/apps/tpbattstat_applet/prefs'

class Prefs():
  def __init__(self, applet):
    self.client = gconf.client_get_default()
    self.gconf_root_key = applet.get_preferences_key()
    if self.gconf_root_key == None:
      self.gconf_root_key = '/apps/tpbattstat_applet'
      self.applySchema('delay')
    else:
      applet.add_preferences(SCHEMA_DIR)
    print self.gconf_root_key
  def applySchema(self, key):   
    schema = gconf.Schema()
#    print dir(self.client)
#    schema.schema_path = SCHEMA_DIR + '/' + key
#    self.client.set_schema(self.gconf_root_key + '/' + key, schema)
  def gconfGetInt(self, key):
    return self.client.get_string(self.gconf_root_key + '/' + key)
  def gconfGetStr(self, key):
    return self.client.get_string(self.gconf_root_key + '/' + key)
  def update(self):
    delay = self.gconfGetInt('delay')
    if delay != None:
      self.delay = delay
    print delay

