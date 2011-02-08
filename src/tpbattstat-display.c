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
    statusIconSet->idle = createPercentIconSet("icons/idle");
    statusIconSet->charging = createPercentIconSet("icons/charging");
    statusIconSet->discharging = createPercentIconSet("icons/discharging");
    return statusIconSet;
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

    if(strlen(status->msg) > 0)
    {
      desktop_log(status->msg);
      g_free(status->msg);
    }

    status->count++;

    char *markup = g_markup_printf_escaped (
        "<tt><small><small><small><small>%d\n%4.1f\n%d</small></small></small></small></tt>",
        status->bat0->remaining_percent,
        power_avg_W,
        status->bat1->remaining_percent);

/*        "%010lu"
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
*/
    return markup;
}


GdkPixbuf *
choose_image (StatusIconSet *statusIconSet, Battery *battery)
{
    PercentIconSet *percentIconSet;
    if(battery->state == CHARGING)
        percentIconSet = statusIconSet->charging;
    else if(battery->state == DISCHARGING)
        percentIconSet = statusIconSet->discharging;
    else
        percentIconSet = statusIconSet->idle;

    GdkPixbuf *pixbuf;
    int per = battery->remaining_percent;
    if(per > 98)
      pixbuf = percentIconSet->per100;
    else if(per > 90)
      pixbuf = percentIconSet->per90;
    else if(per > 80)
      pixbuf = percentIconSet->per80;
    else if(per > 70)
      pixbuf = percentIconSet->per70;
    else if(per > 60)
      pixbuf = percentIconSet->per60;
    else if(per > 50)
      pixbuf = percentIconSet->per50;
    else if(per > 40)
      pixbuf = percentIconSet->per40;
    else if(per > 30)
      pixbuf = percentIconSet->per30;
    else if(per > 20)
      pixbuf = percentIconSet->per20;
    else if(per > 10)
      pixbuf = percentIconSet->per10;
    else if(per > 0)
      pixbuf = percentIconSet->per0;

    return pixbuf;
}

void
update_display (HUD *hud, BatteryStatus *status)
{
    char *markup = get_battery_status_markup(status);
    gtk_label_set_markup(hud->label, markup);
    gtk_image_set_from_pixbuf(
        hud->bat0img, choose_image(hud->statusIconSet, status->bat0));
    gtk_image_set_from_pixbuf(
        hud->bat1img, choose_image(hud->statusIconSet, status->bat1));
    gtk_widget_set_size_request(hud->bat0img, IMAGE_WIDTH, IMAGE_HEIGHT);
    gtk_widget_set_size_request(hud->bat1img, IMAGE_WIDTH, IMAGE_HEIGHT);
    g_free(markup);
}

void
init_display (HUD *hud, PanelApplet *applet)
{
    GtkWidget *hbox = gtk_hbox_new(TRUE, 1);
    hud->label = (GtkLabel*) gtk_label_new("<Status Unread>");
    hud->bat0img = gtk_image_new_from_pixbuf (createIcon("", "none.svg", 12, 12));
    hud->bat1img = gtk_image_new_from_pixbuf (createIcon("", "none.svg", 12, 12));
    hud->statusIconSet = createStatusIconSet();

    gtk_box_pack_start(GTK_BOX(hbox), hud->bat0img, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(hbox), hud->label, TRUE, TRUE, 0);
    gtk_box_pack_start(GTK_BOX(hbox), hud->bat1img, TRUE, TRUE, 0);

    gtk_widget_set_size_request(hud->label, 24, 24);
    gtk_container_add (GTK_CONTAINER (applet), GTK_WIDGET(hbox));
	
    gtk_widget_show_all (GTK_WIDGET (applet));
}

