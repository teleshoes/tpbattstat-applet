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

int
get_digs (unsigned long num)
{
    int d=0;
    while(num > 0)
    {
        num /= 10;
        d++;
    }
    return d;
}

const char *
get_spacer (int desiredLen, unsigned long num)
{
    int digs = get_digs(num);
    switch( desiredLen - digs ) 
    {
        case 10:
            capa++;
        case 'a':
            lettera++;
        default :
            total++;
    }
}


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

    unsigned long count = status->count++;
    int digs = 0;
    
    char *spacer;
    if(count<=9) spacer = "0000";
    else if(count<=99) spacer = "000";
    else if(count<=999) spacer = "00";
    else if(count<=9999) spacer = "0";
    else spacer = "";

    if(strlen(status->msg) > 0)
    {
      desktop_log(status->msg);
      g_free(status->msg);
    }

    char *markup = g_markup_printf_escaped (
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
          bat0color, status->bat0->remaining_percent,
          power_avg_W,
          bat1color, status->bat1->remaining_percent);

    return markup;
}

void
update_display (TPBattStat *tpbattstat)
{
    char *markup = get_battery_status_markup(tpbattstat->status);
    gtk_label_set_markup(tpbattstat->label, markup);
    g_free(markup);
}
