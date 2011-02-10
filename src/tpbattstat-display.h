/**************************************************************************
 *  TPBattStatApplet v0.1
 *  Copyright 2011 Elliot Wolk
 **************************************************************************
 *  This file is part of TPBattStatApplet.
 *
 *  TPBattStatApplet is free software: you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License as
 *  published by the Free Software Foundation, either version 3 of the
 *  License, or (at your option) any later version.
 *
 *  TPBattStatApplet is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with TPBattStatApplet.  If not, see <http://www.gnu.org/licenses/>.
 *************************************************************************/

#ifndef TPBATTSTAT_DISPLAY_H
#define TPBATTSTAT_DISPLAY_H

#include <panel-applet.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <gtk/gtklabel.h>
#include <gtk/gtkimage.h>

#include "tpbattstat-battinfo.h"
#include "tpbattstat-prefs.h"

#define PIXMAP_DIR "/usr/share/pixmaps/tpbattstat-applet"
#define IMAGE_HEIGHT 24
#define IMAGE_WIDTH 24

typedef struct {
   GdkPixbuf *per0; 
   GdkPixbuf *per10; 
   GdkPixbuf *per20; 
   GdkPixbuf *per30; 
   GdkPixbuf *per40; 
   GdkPixbuf *per50; 
   GdkPixbuf *per60; 
   GdkPixbuf *per70; 
   GdkPixbuf *per80; 
   GdkPixbuf *per90; 
   GdkPixbuf *per100; 
} PercentIconSet;

typedef struct {
  GdkPixbuf *none; 
  PercentIconSet *idle;
  PercentIconSet *charging;
  PercentIconSet *discharging;
} StatusIconSet;


typedef struct {
    GtkLabel *label;
    GtkImage *bat0img;
    GtkImage *bat1img;
    StatusIconSet *statusIconSet;
} HUD;

void update_display (HUD *hud, BatteryStatus *status, Prefs *prefs);

void init_display (HUD *hud, PanelApplet *applet);

#endif /* TPBATTSTAT_DISPLAY_H */
