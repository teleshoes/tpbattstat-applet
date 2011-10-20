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
import gtk


class Gconftool():
  def __init__(self):
    self.gconftool = 'gconftool'
  def get(self, *args):
    args = [self.gconftool] + list(args)
    try:
      (stdout, _) = Popen(args, stdout=PIPE).communicate()
      return stdout.rstrip()
    except:
      print >> sys.stderr, 'Could not exec gconftool with args=' + str(args)
      return None
  def set(self, *args):
    args = [self.gconftool] + list(args)
    try:
      Popen(args).wait()
    except:
      print >> sys.stderr, 'Could not exec gconftool with args=' + str(args)
  def long_docs(self, key):
    return self.get('--long-docs', key)
  def get_type(self, key):
    return self.get('--get-type', key)
  def get_list_type(self, key):
    try:
      #may i add that this is ridiculous. where is this option??!
      m = re.match('(.*)/([^/]*)', key)
      keyDir = m.group(1)
      keyName = m.group(2)
      dirDump = self.get('--dump', keyDir)
      m = re.search(
        '<key>' + keyName + '</key>' + '.*?' + '<list type="([a-zA-Z]*)">',
        dirDump,
        flags=re.DOTALL)
      return m.group(1)
    except:
      return None
  def ls_dir(self, keydir):
    try:
      keys = []
      for line in self.get('--all-entries', keydir).split('\n'):
        m = re.match('^ ([a-zA-Z0-9_\-:\^@*]+) = .*$', line)
        if m:
          keys.append(m.group(1))
      return keys
    except:
      return []
  def get_value(self, key):
    return self.get('--get', key)
  def set_value(self, key, value):
    gcType = self.get_type(key)
    value = str(value)
    if gcType == 'list':
      gcTypeList = self.get_list_type(key)
      return self.set(
        '--set', '--type', gcType, '--list-type', gcTypeList, key, value)
    else:
      return self.set('--set', '--type', gcType, key, value)


gconftool = Gconftool()

class GconfRadioButton(gtk.RadioButton):
  def __init__(self, value, group=None, label=None, use_underline=True):
    super(GconfRadioButton, self).__init__(group, label, use_underline)
    self.value = value
  def getValue(self):
    return self.value

class GconfWidget():
  def __init__(self, gcType, numCfg, enum):
    self.gcType = gcType
    self.enum = enum
    if enum == None:
      if gcType == 'int':
        if numCfg == None:
          numCfg = (None, None, None, None)
        (minval, maxval, step, page) = numCfg
        spinAdj = self.intAdj(minval, maxval, step, page)
        if step == None:
          step = 1
        self.widget = gtk.SpinButton(spinAdj, float(step), 0)
        self.getValueFct = self.widget.get_value_as_int
        self.setValueFct = self.setSpinButtonValue
        self.changeSignal = 'value-changed'
      elif gcType == 'float':
        if numCfg == None:
          numCfg = (None, None, None, None)
        (minval, maxval, step, page) = numCfg
        spinAdj = self.floatAdj(minval, maxval, step, page)
        if step == None:
          step = 0.1
        self.widget = gtk.SpinButton(spinAdj, step, 3)
        self.getValueFct = self.widget.get_value
        self.setValueFct = self.setSpinButtonValue
        self.changeSignal = 'value-changed'
      elif gcType == 'bool':
        self.widget = gtk.CheckButton()
        self.getValueFct = self.widget.get_active
        self.setValueFct = self.widget.set_active
        self.changeSignal = 'toggled'
      else:
        self.widget = gtk.Entry()
        self.getValueFct = self.widget.get_text
        self.setValueFct = self.widget.set_text
        self.changeSignal = 'changed'
    else:
      self.widget = gtk.combo_box_new_text()
      self.getValueFct = self.widget.get_active_text
      self.setValueFct = self.setComboBoxValue
      self.changeSignal = 'changed'
      for value in enum:
        self.widget.append_text(value)
  def setSpinButtonValue(self, value):
    if value == None:
      self.widget.set_value(-1.0)
    else:
      self.widget.set_value(float(value))
  def setComboBoxValue(self, value):
    index = -1
    value = str(value)
    for i in range(0, len(self.enum)):
      if self.enum[i] == value:
        index = i
        break
    self.widget.set_active(index)
  def intAdj(self, minval, maxval, step, page):
    if minval == None:
      minval = 0-sys.maxint
    if maxval == None:
      maxval = sys.maxint
    if step == None:
      step = 1
    if page == None:
      page = 10
    initial = 0
    pagesize = 10
    return gtk.Adjustment(float(initial), float(minval), float(maxval),
      float(step), float(page), 0.0)
  def floatAdj(self, minval, maxval, step, page):
    if minval == None:
      minval = float(0-sys.maxint)
    if maxval == None:
      maxval = float(sys.maxint)
    if step == None:
      step = 0.1
    if page == None:
      page = 1.0
    initial = 0.0
    return gtk.Adjustment(initial, minval, maxval, step, page, 0.0)
  def setValue(self, val):
    try:
      if self.gcType == 'int':
        value = int(val)
      elif self.gcType == 'bool':
        if val == 'false':
          value = False
        elif val == 'true':
          value = True
        else:
          value = bool(val)
      elif self.gcType == 'float':
        value = float(val)
      elif self.gcType == 'string':
        value = str(val)
      elif self.gcType == 'list':
        value = str(val)
      else:
        value = None
    except:
      value = None
    self.setValueFct(value)
 
  def getValue(self):
    try:
      val = self.getValueFct()
      if self.gcType == 'int':
        return int(val)
      elif self.gcType == 'bool':
        if val == 'false':
          value = False
        elif val == 'true':
          value = True
        else:
          return bool(val)
      elif self.gcType == 'float':
        return float(val)
      elif self.gcType == 'string':
        return str(val)
      elif self.gcType == 'list':
        return str(val)
      else:
        return None
    except:
      return None
    
 
  
class GconfGuiElem():
  def __init__(self, keyDir, key, schemaDir, schema, default, description,
    numCfg, enum):
    self.keyDir = keyDir
    self.key = key
    self.schemaDir = schemaDir
    self.schema = schema
    self.description = description
    self.default = default
    self.numCfg = numCfg
    self.enum = enum

    self.gconfKey = self.key
    if self.keyDir != None and self.gconfKey != None:
      self.gconfKey = self.keyDir + '/' + self.gconfKey
    if schemaDir != None and schema != None:
      schema = schemaDir + '/' + schema
    
    if self.description == None:
      self.description = gconftool.long_docs(self.gconfKey)
    self.gconfType = gconftool.get_type(self.gconfKey)
    if self.gconfType == 'list':
      self.gconfListType = gconftool.get_list_type(self.gconfKey)
      self.gcType = self.gconfType
    else:
      self.gconfListType = None
      self.gcType = self.gconfType

    self.label = gtk.Label(self.key)
    self.label.set_tooltip_markup(self.getTooltipMarkup())
    self.gconfWidget = self.buildWidget()
    self.loadFromGconf()
    
    self.gconfWidget.widget.connect(
      self.gconfWidget.changeSignal, self.saveToGconf)
    
  def loadFromGconf(self):
    self.gconfWidget.setValue(gconftool.get_value(self.gconfKey))
  def saveToGconf(self, event):
    gconftool.set_value(self.gconfKey, self.gconfWidget.getValue())
    
  def getTooltipMarkup(self):
    tt = ''
    if self.description != None:
      tt = tt + self.description.strip() + '\n'
    key = self.key
    if self.keyDir != None:
      key = self.keyDir + '/' + key
    tt = tt + '<span size="small">' + key + '</span>\n'
    schema = self.schema
    if self.schemaDir != None:
      schema = self.schemaDir + '/' + schema
    tt = tt + '<span size="small">' + schema + '</span>\n'
    return tt
  def getLabel(self):
    return self.label
  def getWidget(self):
    return self.gconfWidget.widget
  def buildWidget(self):
    return GconfWidget(self.gcType, self.numCfg, self.enum)

class GconfGui(gtk.VBox):
  def __init__(self, keyDir, schemaDir, keyInfo):
    super(GconfGui, self).__init__()
    table = gtk.Table(rows=len(keyInfo), columns=2)
    self.add(table)
    row = 0

    for (key, schema, default, description, numCfg, enum) in keyInfo:
      elem = GconfGuiElem(
        keyDir, key, schemaDir, schema, default, description, numCfg, enum)
      row = row + 1
      table.attach(elem.getLabel(), 0, 1, row, row+1)
      table.attach(elem.getWidget(), 1, 2, row, row+1)

    msg = ''
    if keyDir != None:
      msg += "\ngconf keys: " + keyDir
    if schemaDir != None:
      msg += "\ngconf schemas: " + schemaDir
    if msg != '':
      headerLabel = gtk.Label(msg)
      headerLabel.set_selectable(True)
      row = row + 1
      table.attach(headerLabel, 0, 1, row, row+1)

