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
import gtk

class GuiPrefs(gtk.VBox):
  def __init__(self, prefs):
    super(GuiPrefs, self).__init__()
    self.prefs = prefs

    align = gtk.Alignment(0, 0.5, 0, 0)
    self.table = gtk.Table(rows=len(self.prefs.prefsArr), columns=2)
    self.add(self.table)
    self.curRow = -1
    self.curCol = -1
    self.colors = {
      'lightgrey': gtk.gdk.Color(10000, 10000, 10000),
      'darkgrey': gtk.gdk.Color(50000, 50000, 50000)
    }

    self.messageLabel = gtk.Label()
    self.nextRow()
    self.addCell(self.messageLabel, 2)
    self.prefRows = []

    for pref in self.prefs.prefsArr:
      prefRow = PrefRow(pref, prefs, self.messageLabel)
      self.prefRows.append(prefRow)
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
  def update(self, quiet=True):
    self.prefs.update()
    for prefRow in self.prefRows:
      prefRow.update(quiet)
    self.messageLabel.set_text('')

class PrefRow():
  def __init__(self, pref, prefs, messageLabel):
    self.pref = pref
    self.prefs = prefs
    self.messageLabel = messageLabel

    self.label = gtk.Label()
    self.label.set_markup(self.getLabelMarkup())
    self.label.set_tooltip_markup(self.getTooltipMarkup())
    self.prefWidget = self.buildWidget()

    self.ignoreChanges = False
    self.prefWidget.widget.connect(self.prefWidget.changeSignal, self.savePref)
    self.error = None
  def getLabelMarkup(self):
    return (self.pref.name + '\n'
      + self.smallText(self.pref.valType + ' - ' + self.pref.shortDesc))
  def savePref(self, w):
    if self.ignoreChanges:
      return
    print '..saving prefs'

    try:
      self.prefs.readPrefsFile()
    except:
      pass
    try:
      self.prefs[self.pref.name] = self.prefWidget.getValueFct()
      self.prefs.writePrefsFile()
      self.prefs.readPrefsFile()
      self.messageLabel.set_markup('saved ' + self.pref.name)
      print 'saved!'
    except Exception as e:
      self.messageLabel.set_text('ERROR: ' + e.message)
      print 'prefs not saved: ' + e.message

  def smallText(self, msg):
    return '<span size="small">' + msg + '</span>'
  def getTooltipMarkup(self):
    msg = '(default=' + str(self.pref.default) + ')\n'
    if self.pref.longDesc != None:
      msg += self.pref.longDesc
    else:
      msg += self.pref.shortDesc
    return msg
  def getLabel(self):
    return self.label
  def getWidget(self):
    return self.prefWidget.widget
  def buildWidget(self):
    return PrefWidget(self.pref.valType, self.pref.enum)
  def update(self, quiet):
    if quiet:
      self.ignoreChanges = True
    self.prefWidget.setValueFct(self.prefs[self.pref.name])
    self.ignoreChanges = False

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
    elif valType == 'string':
      self.widget = gtk.Entry()
      self.getValueFct = self.widget.get_text
      self.setValueFct = self.widget.set_text
      self.changeSignal = 'changed'
    elif valType[:5] == 'list-':
      self.widget = gtk.Entry()
      self.getValueFct = self.widget.get_text
      self.setValueFct = self.setListValue
      self.changeSignal = 'changed'
  def setListValue(self, vals):
    s = '['
    for i in range(len(vals)):
      s += str(vals[i])
      if i != len(vals)-1:
        s += ','
    s += ']'
    self.widget.set_text(s)
  def setSpinButtonValue(self, value):
    if value == None:
      self.widget.set_value(-1.0)
    else:
      self.widget.set_value(float(value))
  def setComboBoxValue(self, value):
    index = -1
    i = 0
    for name in self.enum.names:
      if str(name) == str(value):
        index = i
        break
      i += 1
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
