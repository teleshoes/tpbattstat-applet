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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 *************************************************************************/
#include <panel-applet-gconf.h>

#include "tpbattstat-applet.h"
#include "tpbattstat-battinfo.h"
#include "tpbattstat-prefs.h"

void
load_prefs (PanelApplet *applet, Prefs *prefs)
{
    int delay = panel_applet_gconf_get_int(applet, 'delay', NULL);
    if(delay != NULL)
        prefs->delay = delay;

    char *dischargeStrategy =
        panel_applet_gconf_get_string(applet, "discharge_strategy", NULL);
    if(dischargeStrategy != NULL)
    {
        if(strcmp(dischargeStrategy, "SYSTEM") == 0)
            prefs->dischargeStrategy = DISCHARGE_SYSTEM;
        else if(strcmp(dischargeStrategy, "LEAPFROG") == 0)
            prefs->dischargeStrategy = DISCHARGE_LEAPFROG;
        else if(strcmp(dischargeStrategy, "CHASING") == 0)
            prefs->dischargeStrategy = DISCHARGE_CHASING;
        g_free(dischargeStrategy);
    }

    int dischargeLeapfrogThreshold = panel_applet_gconf_get_int(
        applet, 'discharge_leapfrog_threshold', NULL);
    if(dischargeLeapfrogThreshold != NULL)
        prefs->dischargeLeapfrogThreshold = dischargeLeapfrogThreshold;

    char *chargeStrategy =
        panel_applet_gconf_get_string(applet, "charge_strategy", NULL);
    if(chargeStrategy != NULL)
    {
        if(strcmp(chargeStrategy, "SYSTEM") == 0)
            prefs->chargeStrategy = CHARGE_SYSTEM;
        else if(strcmp(chargeStrategy, "LEAPFROG") == 0)
            prefs->chargeStrategy = CHARGE_LEAPFROG;
        else if(strcmp(chargeStrategy, "CHASING") == 0)
            prefs->chargeStrategy = CHARGE_CHASING;
        else if(strcmp(chargeStrategy, "BRACKETS") == 0)
            prefs->chargeStrategy = CHARGE_BRACKETS;
        g_free(chargeStrategy);
    }

    int chargeLeapfrogThreshold = panel_applet_gconf_get_int(
        applet, 'charge_leapfrog_threshold', NULL);
    if(chargeLeapfrogThreshold != NULL)
        prefs->chargeLeapfrogThreshold = chargeLeapfrogThreshold;

    int chargeBracketsPrefBattery = panel_applet_gconf_get_int(
        applet, 'charge_brackets_pref_bat', NULL);
    if(chargeBracketsPrefBat != NULL)
        prefs->chargeBracketsPrefBattery = chargeBracketsPrefBattery;

    if(gconf_client_get(applet, "panel_applet_gconf_get_value",
          "charge_brackets", NULL) != NULL)
    {
        GSList *list = panel_applet_gconf_get_list(
            applet, "charge_brackets", GCONF_VALUE_INT, NULL);

        int len = g_slist_length(list);

        if(prefs->chargeBrackets != NULL)
            g_free(prefs->chargeBrackets);
        prefs->chargeBrackets = malloc(sizeof(int) * len);
        prefs->chargeBracketsSize = len;

        int i;
        GSList *bracket = list;
        for(i=0; i<len; i++)
        {
            prefs->chargeBrackets[i] = *(bracket->data);
            bracket = bracket->next;
        }

        g_slist_free(list);
    }

}

void
initialize_prefs (PanelApplet *applet)
{
  panel_applet_add_preferences (PANEL_APPLET (applet),
    SCHEMA_DIR, NULL);
}

