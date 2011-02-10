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
#include <gtk/gtkbox.h>
#include <gtk/gtkwidget.h>
#include <gdk-pixbuf/gdk-pixbuf.h>
#include <gtk/gtkimage.h>

#include <panel-applet.h>

#include "tpbattstat-battinfo.h"
#include "tpbattstat-display.h"
#include "tpbattstat-prefs.h"

GdkPixbuf *
createIcon (const char *basedir, const char *file, int width, int height)
{
    int len = strlen(PIXMAP_DIR) + 1 +
      strlen(basedir) + 1 +
      strlen(file) + 1;
    char *filepath = malloc(len * sizeof(char));
    strcpy(filepath, PIXMAP_DIR);
    strcat(filepath, "/");
    strcat(filepath, basedir);
    strcat(filepath, "/");
    strcat(filepath, file);

    GdkPixbuf *pixbuf =	gdk_pixbuf_new_from_file(filepath, NULL);
    g_free(filepath);
    
    if(pixbuf != NULL)
    {
      pixbuf = gdk_pixbuf_scale_simple(
        pixbuf,
        width,
        height,
        GDK_INTERP_BILINEAR);
    }

    return pixbuf;
}

PercentIconSet *
createPercentIconSet (const char *basedir)
{
    PercentIconSet *ret = malloc(sizeof(PercentIconSet));
    ret->per0 = createIcon(basedir, "0.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per10 = createIcon(basedir, "10.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per20 = createIcon(basedir, "20.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per30 = createIcon(basedir, "30.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per40 = createIcon(basedir, "40.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per50 = createIcon(basedir, "50.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per60 = createIcon(basedir, "60.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per70 = createIcon(basedir, "70.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per80 = createIcon(basedir, "80.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per90 = createIcon(basedir, "90.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    ret->per100 = createIcon(basedir, "100.svg", IMAGE_WIDTH, IMAGE_HEIGHT);
    return ret;
}

StatusIconSet *
createStatusIconSet ()
{
    StatusIconSet *statusIconSet = malloc(sizeof(StatusIconSet));
    statusIconSet->none = createIcon("icons", "none.svg",
      IMAGE_WIDTH, IMAGE_HEIGHT);

    statusIconSet->idle = createPercentIconSet("icons/idle");
    statusIconSet->charging = createPercentIconSet("icons/charging");
    statusIconSet->discharging = createPercentIconSet("icons/discharging");
    return statusIconSet;
}

char *
get_battery_status_markup (BatteryStatus *status, Prefs *prefs)
{
    if(strlen(status->msg) > 0)
    {
      desktop_log(status->msg);
      g_free(status->msg);
    }

    status->count++;

    int bat0rem = status->bat0->remaining_percent;
    int bat1rem = status->bat1->remaining_percent;

    char *bat0display;
    if(prefs->displayColoredText && status->bat0->state != IDLE)
    {
        const char *color;
        if(status->bat0->state == CHARGING)
            color = "#60FF60";
        else if(status->bat0->state == DISCHARGING)
            color = "#FF6060";
        else
            color = "white";

        bat0display = malloc(33 + strlen(color) + 3 + 1);
        sprintf(bat0display,
          "<b><span foreground='%s'>%d</span></b>",
          color,
          bat0rem);
    }
    else
    {
        bat0display = malloc(3 + 1);
        sprintf(bat0display, "%d", bat0rem);
    }
    char *bat1display;
    if(prefs->displayColoredText && status->bat1->state != IDLE)
    {
        const char *color;
        if(status->bat1->state == CHARGING)
            color = "#60FF60";
        else if(status->bat1->state == DISCHARGING)
            color = "#FF6060";
        else
            color = "white";

        bat1display = malloc(33 + strlen(color) + 3 + 1);
        sprintf(bat1display,
          "<b><span foreground='%s'>%d</span></b>",
          color,
          bat1rem);
    }
    else
    {
        bat1display = malloc(3 + 1);
        sprintf(bat1display, "%d", bat1rem);
    }

    const char *size;
    if(bat0rem == 100 && bat1rem == 100)
        size = "xx-small";
    else if(bat0rem == 100 || bat1rem == 100)
        size = "x-small";
    else
        size = "small";

    const char *sep;
    if(prefs->displayBlinkingIndicator && status->count % 2 == 0)
        sep = "<span foreground='blue'>^</span>";
    else
        sep = "^";

    char *power_avg = malloc(64);
    if(prefs->displayPowerAvg)
    {
        int pow0 = status->bat0->power_avg;
        int pow1 = status->bat1->power_avg;
        int powActive = 0;
        if(powActive != 0 && status->bat0->state != IDLE)
            powActive = pow0;
        if(powActive != 0 && status->bat1->state != IDLE)
            powActive = pow1;
        if(pow0 != 0)
            powActive = pow0;
        if(pow1 != 0)
            powActive = pow1;

        float power_avg_W = powActive / 1000.0;

        sprintf(power_avg,
          "\n<span size='xx-small'>   %4.1fW</span>",
          power_avg_W);
    }
    else
        sprintf(power_avg, "");


    char *markup = malloc(
      21 +
      strlen(size) +
      strlen(bat0display) +
      strlen(sep) +
      strlen(bat1display) +
      strlen(power_avg) +
      1);
    sprintf(markup,
      "<span size='%s'>%s%s%s</span>%s",
      size,
      bat0display,
      sep,
      bat1display,
      power_avg);

    g_free(power_avg);

    return markup;
}


GdkPixbuf *
choose_image (StatusIconSet *statusIconSet,
    int installed, int remaining_percent, enum BatteryState state)
{
    if(installed != 1)
        return statusIconSet->none;

    PercentIconSet *percentIconSet;
    if(state == CHARGING)
        percentIconSet = statusIconSet->charging;
    else if(state == DISCHARGING)
        percentIconSet = statusIconSet->discharging;
    else
        percentIconSet = statusIconSet->idle;

    GdkPixbuf *pixbuf;
    if(remaining_percent >= 98)
      pixbuf = percentIconSet->per100;
    else if(remaining_percent >= 90)
      pixbuf = percentIconSet->per90;
    else if(remaining_percent >= 80)
      pixbuf = percentIconSet->per80;
    else if(remaining_percent >= 70)
      pixbuf = percentIconSet->per70;
    else if(remaining_percent >= 60)
      pixbuf = percentIconSet->per60;
    else if(remaining_percent >= 50)
      pixbuf = percentIconSet->per50;
    else if(remaining_percent >= 40)
      pixbuf = percentIconSet->per40;
    else if(remaining_percent >= 30)
      pixbuf = percentIconSet->per30;
    else if(remaining_percent >= 20)
      pixbuf = percentIconSet->per20;
    else if(remaining_percent >= 10)
      pixbuf = percentIconSet->per10;
    else if(remaining_percent >= 0)
      pixbuf = percentIconSet->per0;
    else
      pixbuf = statusIconSet->none;

    return pixbuf;
}

void
update_display (HUD *hud, BatteryStatus *status, Prefs *prefs)
{
    char *markup = get_battery_status_markup(status, prefs);
    gtk_label_set_markup(hud->label, markup);
    g_free(markup);
    if(prefs->displayIcons && prefs->displayOnlyOneIcon)
    {
        gtk_widget_set_visible(GTK_WIDGET(hud->bat0img), 1);
        gtk_widget_set_visible(GTK_WIDGET(hud->bat1img), 0);
        int installed = status->bat0->installed;
        if(installed != 1)
            installed = status->bat1->installed;
        enum BatteryState state = status->bat0->state;
        if(state == IDLE)
            state = status->bat1->state;
        int cap_total = 0;
        int cap_rem = 0;
        if(status->bat0->installed && status->bat0->remaining_capacity > 0)
        {
            int cap = status->bat0->last_full_capacity;
            int rem = status->bat0->remaining_capacity;
            if(cap <= 0 || cap < rem)
                cap = status->bat0->design_capacity;
            if(cap > 0 && cap >= rem)
            {
                cap_total += cap;
                cap_rem += rem;
            }
        } 
        if(status->bat1->installed && status->bat1->remaining_capacity > 0)
        {
            int cap = status->bat1->last_full_capacity;
            int rem = status->bat1->remaining_capacity;
            if(cap <= 0 || cap < rem)
                cap = status->bat1->design_capacity;
            if(cap > 0 && cap >= rem)
            {
                cap_total += cap;
                cap_rem += rem;
            }
        }
        int rem_per = 100 * cap_rem / cap_total;

        gtk_image_set_from_pixbuf(
            hud->bat0img,
            choose_image(
              hud->statusIconSet,
              installed,
              rem_per,
              state));
    }
    else if(prefs->displayIcons && !prefs->displayOnlyOneIcon)
    {
        gtk_widget_set_visible(GTK_WIDGET(hud->bat0img), 1);
        gtk_widget_set_visible(GTK_WIDGET(hud->bat1img), 1);
        gtk_image_set_from_pixbuf(
            hud->bat0img,
            choose_image(hud->statusIconSet,
              status->bat0->installed,
              status->bat0->remaining_percent,
              status->bat0->state));
        gtk_image_set_from_pixbuf(
            hud->bat1img,
            choose_image(hud->statusIconSet,
              status->bat1->installed,
              status->bat1->remaining_percent,
              status->bat1->state));
    }
    else
    {
        gtk_widget_set_visible(GTK_WIDGET(hud->bat0img), 0);
        gtk_widget_set_visible(GTK_WIDGET(hud->bat1img), 0);
    }
}

void
init_display (HUD *hud, PanelApplet *applet)
{
    GtkWidget *hbox = gtk_hbox_new(TRUE, 1);
    hud->label = (GtkLabel*) gtk_label_new("<Status Unread>");
    
    hud->statusIconSet = createStatusIconSet();
    hud->bat0img = GTK_IMAGE(
        gtk_image_new_from_pixbuf(hud->statusIconSet->none));
    hud->bat1img = GTK_IMAGE(
        gtk_image_new_from_pixbuf(hud->statusIconSet->none));
    
    gtk_widget_set_size_request(GTK_WIDGET(hud->bat0img),
      IMAGE_WIDTH, IMAGE_HEIGHT);
    gtk_widget_set_size_request(GTK_WIDGET(hud->label), 35, 24);
    gtk_widget_set_size_request(GTK_WIDGET(hud->bat1img),
      IMAGE_WIDTH, IMAGE_HEIGHT);

    gtk_box_pack_start(GTK_BOX(hbox), GTK_WIDGET(hud->bat0img),
      TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(hbox), GTK_WIDGET(hud->label),
      TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(hbox), GTK_WIDGET(hud->bat1img),
      TRUE, TRUE, 0);

    gtk_container_add (GTK_CONTAINER (applet), GTK_WIDGET(hbox));
	
    gtk_widget_show_all (GTK_WIDGET (applet));
}

