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

#include <gtk/gtk.h>
//#include <panel-applet.h>

//#include "tpbattstat-battinfo.h"
//#include "tpbattstat-display.h"

char *
get_battery_status_markup (BatteryStatus *status)
{
    char *bat0color;
    if(status->bat0->state == IDLE)             bat0color = "black";
    else if(status->bat0->state == CHARGING)    bat0color = "green";
    else if(status->bat0->state == DISCHARGING) bat0color = "red";
    char *bat1color;
    if(status->bat1->state == IDLE)             bat1color = "black";
    else if(status->bat1->state == CHARGING)    bat1color = "green";
    else if(status->bat1->state == DISCHARGING) bat1color = "red";

    float power_avg_W = status->bat0->power_avg / 1000.0;
    if(power_avg_W == 0)
        power_avg_W = status->bat1->power_avg / 1000.0;

    if(strlen(status->msg) > 0)
    {
      desktop_log(status->msg);
      g_free(status->msg);
    }

    status->count++;

    char *markup = g_markup_printf_escaped (
        "%010lu"
        "<tt>"
        "<span style=\"italic\" "
          "font_weight=\"bold\" "
          "fgcolor=\"white\" "
          "bgcolor=\"%s\">%d%%</span>"
        "<small> %4.1fW </small>"
        "<span style=\"italic\" "
          "font_weight=\"bold\" "
          "fgcolor=\"white\" "
          "bgcolor=\"%s\">%d%%</span>"
        "</tt>",
        status->count,
        bat0color, status->bat0->remaining_percent,
        power_avg_W,
        bat1color, status->bat1->remaining_percent);

    return markup;
}

void
update_display (HUD *hud, BatteryStatus *status)
{
    char *markup = get_battery_status_markup(status);
    gtk_label_set_markup(hud->label, markup);
    g_free(markup);
}

void
init_display (HUD *hud, PanelApplet *applet)
{
    hud->label = (GtkLabel*) gtk_label_new("<Status Unread>");
	gtk_container_add (GTK_CONTAINER (applet), GTK_WIDGET(hud->label));
	gtk_widget_show_all (GTK_WIDGET (applet));
}

