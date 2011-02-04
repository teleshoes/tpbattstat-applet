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

#include <string.h>

#include <panel-applet.h>
#include <gtk/gtklabel.h>
#include <gtk/gtkbox.h>
#include <gtk/gtkimage.h>
#include <gtk/gtk.h>
#include <gtk/gtkstock.h>

#include <glib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>

#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>
#include <dirent.h>
#include <string.h>
#include <time.h>
#include <glib.h>
#include <gdk/gdkx.h>
#include <gtk/gtk.h>
#include <panel-applet.h>

#include "tpbattstat-applet.h"
#include "tpbattstat-battinfo.h"
#include "tpbattstat-display.h"
#include "tpbattstat-prefs.h"

void
desktop_log (char *msg)
{
    char *cmd = malloc(256);
    sprintf(cmd, "echo `date`: \"%s\" >> /home/wolke/Desktop/out", msg);
    system(cmd);
    g_free(cmd);
} 

void
verb_statistics (BonoboUIComponent *ui_container,
               gpointer           user_data,
               const              char *cname)
{
    system("gnome-power-statistics &");
}
const char context_menu_xml [] =
    "<popup name=\"button3\">\n"
    "   <menuitem name=\"Properties Item\" "
    "             verb=\"Statistics\" "
    "           _label=\"_Statistics\"\n"
    "          pixtype=\"stock\" "
    "          pixname=\"gtk-properties\"/>\n"
    "</popup>\n";
const BonoboUIVerb context_menu_verbs [] = {
        BONOBO_UI_VERB ("Statistics", verb_statistics),
        BONOBO_UI_VERB_END
};




gboolean
update (TPBattStat *tpbattstat)
{
    int newDelay = tpbattstat->prefs->delay;
    if(newDelay > 0 && newDelay != tpbattstat->currentDelay)
    {
        start_update(tpbattstat);
        return FALSE;
    }

    get_battery_status(tpbattstat->status);

    load_prefs(tpbattstat->applet, tpbattstat->prefs);

    tpbattstat->status->msg = "";
    perhaps_inhibit_charge(
            tpbattstat->status,
            tpbattstat->prefs->chargeStrategy,
            tpbattstat->prefs->chargeLeapfrogThreshold,
            tpbattstat->prefs->chargeBrackets,
            tpbattstat->prefs->chargeBracketsSize,
            tpbattstat->prefs->chargeBracketsPrefBattery);
    perhaps_force_discharge(
            tpbattstat->status,
            tpbattstat->prefs->dischargeStrategy,
            tpbattstat->prefs->dischargeLeapfrogThreshold);

    update_display(tpbattstat);

    return TRUE;
}

gboolean
stop_update (TPBattStat *tpbattstat)
{
    if(tpbattstat->timer != -1)
        g_source_remove (tpbattstat->timer);

    tpbattstat->timer = -1;

    return TRUE;
}

gboolean
start_update(TPBattStat *tpbattstat)
{
    stop_update (tpbattstat);

    tpbattstat->currentDelay = tpbattstat->prefs->delay;
    if(tpbattstat->currentDelay <= 0)
        tpbattstat->currentDelay = 1000;
    update(tpbattstat);
    tpbattstat->timer = g_timeout_add (
        tpbattstat->currentDelay,
        (GSourceFunc) update,
        tpbattstat);

    return TRUE;
}


gboolean
tpbattstat_applet_fill (PanelApplet *applet,
   const gchar *iid,
   gpointer data)
{
	if (strcmp (iid, "OAFIID:TPBattStatApplet") != 0)
		return FALSE;

    initialize_prefs(applet);
    
    TPBattStat *tpbattstat = g_new0(TPBattStat, 1);
    tpbattstat->applet = applet;

    tpbattstat->label = (GtkLabel*) gtk_label_new("<Status Unread>");
	gtk_container_add (GTK_CONTAINER (applet), GTK_WIDGET(tpbattstat->label));
	gtk_widget_show_all (GTK_WIDGET (applet));


    panel_applet_setup_menu (PANEL_APPLET (applet),
	                         context_menu_xml,
	                         context_menu_verbs,
	                         applet);	
    
    tpbattstat->status = malloc(sizeof(BatteryStatus));
    tpbattstat->status->count = 0;
    tpbattstat->status->bat0 = malloc(sizeof(Battery));
    tpbattstat->status->bat1 = malloc(sizeof(Battery));

    tpbattstat->prefs = malloc(sizeof(Prefs));
    load_prefs(tpbattstat->applet, tpbattstat->prefs);

    start_update(tpbattstat);
	
	return TRUE;
}

PANEL_APPLET_BONOBO_FACTORY ("OAFIID:TPBattStatApplet_Factory",
                             PANEL_TYPE_APPLET,
                             "ThinkPad Battery Status Applet",
                             "0",
                             tpbattstat_applet_fill,
                             NULL);
