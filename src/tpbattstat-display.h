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
#include <gtk/gtklabel.h>
#include <gtk/gtkbox.h>
#include <gtk/gtkimage.h>

#include "tpbattstat-battinfo.h"

typedef struct {
    GtkLabel *label;
} HUD;

void update_display (HUD *hud, BatteryStatus *status);

void init_display (HUD *hud, PanelApplet *applet);

#endif /* TPBATTSTAT_DISPLAY_H */
