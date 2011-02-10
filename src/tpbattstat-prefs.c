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

#include <panel-applet.h>
#include <panel-applet-gconf.h>

#include "tpbattstat-prefs.h"

gboolean
valueExists (PanelApplet *applet, const char *key)
{
    GConfValue *val = panel_applet_gconf_get_value(applet, key, NULL);
    gboolean exists = val != NULL;
    return exists;
}

void
load_prefs (PanelApplet *applet, Prefs *prefs)
{
    int delay = panel_applet_gconf_get_int(applet, "delay", NULL);
    if(valueExists(applet, "delay"))
        prefs->delay = delay;

    char *dischargeStrategy =
        panel_applet_gconf_get_string(applet, "discharge_strategy", NULL);
    if(dischargeStrategy != NULL)
    {
        if(strcasecmp(dischargeStrategy, "SYSTEM") == 0)
            prefs->dischargeStrategy = DISCHARGE_SYSTEM;
        else if(strcasecmp(dischargeStrategy, "LEAPFROG") == 0)
            prefs->dischargeStrategy = DISCHARGE_LEAPFROG;
        else if(strcasecmp(dischargeStrategy, "CHASING") == 0)
            prefs->dischargeStrategy = DISCHARGE_CHASING;
        g_free(dischargeStrategy);
    }

    int dischargeLeapfrogThreshold = panel_applet_gconf_get_int(
        applet, "discharge_leapfrog_threshold", NULL);
    if(dischargeLeapfrogThreshold > 0)
        prefs->dischargeLeapfrogThreshold = dischargeLeapfrogThreshold;

    char *chargeStrategy =
        panel_applet_gconf_get_string(applet, "charge_strategy", NULL);
    if(chargeStrategy != NULL)
    {
        if(strcasecmp(chargeStrategy, "SYSTEM") == 0)
            prefs->chargeStrategy = CHARGE_SYSTEM;
        else if(strcasecmp(chargeStrategy, "LEAPFROG") == 0)
            prefs->chargeStrategy = CHARGE_LEAPFROG;
        else if(strcasecmp(chargeStrategy, "CHASING") == 0)
            prefs->chargeStrategy = CHARGE_CHASING;
        else if(strcasecmp(chargeStrategy, "BRACKETS") == 0)
            prefs->chargeStrategy = CHARGE_BRACKETS;
        g_free(chargeStrategy);
    }

    int chargeLeapfrogThreshold = panel_applet_gconf_get_int(
        applet, "charge_leapfrog_threshold", NULL);
    if(chargeLeapfrogThreshold > 0)
        prefs->chargeLeapfrogThreshold = chargeLeapfrogThreshold;

    int chargeBracketsPrefBattery = panel_applet_gconf_get_int(
        applet, "charge_brackets_pref_bat", NULL);
    if(chargeBracketsPrefBattery > 0)
        prefs->chargeBracketsPrefBattery = chargeBracketsPrefBattery;
    else
        prefs->chargeBracketsPrefBattery = 0;

    if(valueExists(applet, "charge_brackets"))
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
            prefs->chargeBrackets[i] = GPOINTER_TO_INT(bracket->data);
            bracket = bracket->next;
        }

        g_slist_free(list);
    }

    int displayPowerAvg = panel_applet_gconf_get_bool(
      applet, "display_power_avg", NULL);
    if(valueExists(applet, "display_power_avg"))
        prefs->displayPowerAvg = displayPowerAvg;

    int displayColoredText = panel_applet_gconf_get_bool(
      applet, "display_colored_text", NULL);
    if(valueExists(applet, "display_colored_text"))
        prefs->displayColoredText = displayColoredText;

    int displayIcons = panel_applet_gconf_get_bool(
      applet, "display_icons", NULL);
    if(valueExists(applet, "display_icons"))
        prefs->displayIcons = displayIcons;

    int displayOnlyOneIcon = panel_applet_gconf_get_bool(
      applet, "display_only_one_icon", NULL);
    if(valueExists(applet, "display_only_one_icon"))
        prefs->displayOnlyOneIcon = displayOnlyOneIcon;

    int displayBlinkingIndicator = panel_applet_gconf_get_bool(
      applet, "display_blinking_indicator", NULL);
    if(valueExists(applet, "display_blinking_indicator"))
        prefs->displayBlinkingIndicator = displayBlinkingIndicator;
}

void
initialize_prefs (PanelApplet *applet)
{
  panel_applet_add_preferences (PANEL_APPLET (applet),
    SCHEMA_DIR, NULL);
}

