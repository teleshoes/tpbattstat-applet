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

class GuiPrefs(gtk.VBox):
  def __init__(self, prefs):
    super(GuiPrefs, self).__init__()
    self.prefs = prefs

    align = gtk.Alignment(0, 0.5, 0, 0)
    self.table = gtk.Table(rows=len(self.prefs.names), columns=2)
    self.add(self.table)
    self.curRow = -1
    self.curCol = -1
    self.colors = {
      'lightgrey': gtk.gdk.Color(10000, 10000, 10000),
      'darkgrey': gtk.gdk.Color(50000, 50000, 50000)
    }

    for pref in self.prefs.names:
      prefRow = PrefRow(
        pref,
        self.prefs.types[pref],
        self.prefs.defaults[pref],
        self.prefs.enums[pref],
        self.prefs.shortDescs[pref],
        self.prefs.longDescs.get(pref))
      self.nextRow()
      prefRow.getLabel().set_alignment(0, 0)
      self.addCell(prefRow.getLabel(), 1)
      self.addCell(prefRow.getWidget(), 1)

    msg = '{you can also edit the conf file at: ' + self.prefs.prefsFile + '}'
    if msg != '':
      self.nextRow()
      self.addCell(gtk.Label(msg), 2)
  def nextRow(self):
    self.curCol = -1
    self.curRow += 1
  def rowColor(self):
    if self.curRow % 2 == 0:
      return (self.colors['lightgrey'], self.colors['darkgrey'])
    else:
      return (self.colors['darkgrey'], self.colors['lightgrey'])
  def addBanner(self, w):
    self.table.attach(w, 0, 2, self.curRow, self.curRow+1)
  def addCell(self, w, colWidth):
    self.curCol += 1
    eb = gtk.EventBox()
    (bgColor, fgColor) = self.rowColor()
    if bgColor != None:
      eb.modify_bg(gtk.STATE_NORMAL, bgColor)
    if fgColor != None:
      eb.modify_fg(gtk.STATE_NORMAL, fgColor)
    w.modify_fg(gtk.STATE_NORMAL, fgColor)
    eb.add(w)
    (col, row) = (self.curCol, self.curRow)
    self.table.attach(eb, col, col+colWidth, row, row+1)

class PrefRow():
  def __init__(self, key, valType, default, enum, shortDesc, longDesc):
    self.key = key
    self.valType = valType
    self.default = default
    self.enum = enum
    self.shortDesc = shortDesc
    self.longDesc = longDesc

    self.label = gtk.Label()
    self.label.set_markup(self.getLabelMarkup())
    self.label.set_tooltip_markup(self.getTooltipMarkup())
    self.prefWidget = self.buildWidget()

    self.prefWidget.widget.connect(
    self.prefWidget.changeSignal, self.savePref)
  def getLabelMarkup(self):
    return (self.key + '\n'
      + self.smallText(self.valType + ' - ' + self.shortDesc))
  def savePref(self, val):
    pass
  def smallText(self, msg):
    return '<span size="small">' + msg + '</span>'
  def getTooltipMarkup(self):
    if self.longDesc != None:
      return self.longDesc
    else:
      return self.shortDesc
  def getLabel(self):
    return self.label
  def getWidget(self):
    return self.prefWidget.widget
  def buildWidget(self):
    return PrefWidget(self.valType, self.enum)

class GconfRadioButton(gtk.RadioButton):
  def __init__(self, value, group=None, label=None, use_underline=True):
    super(GconfRadioButton, self).__init__(group, label, use_underline)
    self.value = value
  def getValue(self):
    return self.value

class PrefWidget():
  def __init__(self, valType, enum):
    self.valType = valType
    self.enum = enum
    (minval, maxval, step, page) = (None, None, 5, 20)
    spinAdj = self.intAdj(minval, maxval, step, page)
    if valType == 'int':
      self.widget = gtk.SpinButton(spinAdj, float(step), 0)
      self.getValueFct = self.widget.get_value_as_int
      self.setValueFct = self.setSpinButtonValue
      self.changeSignal = 'value-changed'
    elif valType == 'float':
      self.widget = gtk.SpinButton(spinAdj, step, 3)
      self.getValueFct = self.widget.get_value
      self.setValueFct = self.setSpinButtonValue
      self.changeSignal = 'value-changed'
    elif valType == 'bool':
      self.widget = gtk.CheckButton()
      self.getValueFct = self.widget.get_active
      self.setValueFct = self.widget.set_active
      self.changeSignal = 'toggled'
    elif valType == 'enum':
      self.widget = gtk.combo_box_new_text()
      self.getValueFct = self.widget.get_active_text
      self.setValueFct = self.setComboBoxValue
      self.changeSignal = 'changed'
      for name in enum.names:
        self.widget.append_text(name)
    else:
      self.widget = gtk.Entry()
      self.getValueFct = self.widget.get_text
      self.setValueFct = self.widget.set_text
      self.changeSignal = 'changed'
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
      if self.valType == 'int':
        value = int(val)
      elif self.valType == 'bool':
        if val == 'false':
          value = False
        elif val == 'true':
          value = True
        else:
          value = bool(val)
      elif self.valType == 'float':
        value = float(val)
      elif self.valType == 'string':
        value = str(val)
      elif self.valType == 'list':
        value = str(val)
      else:
        value = None
    except:
      value = None
    self.setValueFct(value)
 
  def getValue(self):
    try:
      val = self.getValueFct()
      if self.valType == 'int':
        return int(val)
      elif self.valType == 'bool':
        if val == 'false':
          value = False
        elif val == 'true':
          value = True
        else:
          return bool(val)
      elif self.valType == 'float':
        return float(val)
      elif self.valType == 'string':
        return str(val)
      elif self.valType == 'list':
        return str(val)
      else:
        return None
    except:
      return None 
