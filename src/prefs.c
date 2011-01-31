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

enum DischargeStrategy {
    DISCHARGE_SYSTEM, /*
       -never force, let the system decide
         {this probably means BAT1 all the way, then BAT0 all the way}*/

    DISCHARGE_LEAPFROG, /*
       -if one battery was forcibly being discharging,
         forcibly discharge it unless that battery has rem_percent that
         is less than the other by an amount greater than the threshold
       -otherwise, force the battery with larger rem_percent
       -will never forcibly discharge a battery with rem_percent less
         than the threshold
        e.g: (threshold=3)
          50 49 48 47 46......................46 45 44 43 42 41 40 39 38
            ^  ^  ^  ^  v  v  v  v  v  v  v  v  ^  ^  ^  ^  ^  ^  ^  ^
          50..........50 49 48 47 46 45 44 43 42......................42*/

    DISCHARGE_CHASING /*
       -if one battery has rem_percent that is bigger than the other,
         force that battery to discharge
       -otherwise, allow the system default to discharge */
};



enum ChargeStrategy {
    CHARGE_SYSTEM, /*
       -never inhibit charge, let the system decide
         {this probably means keep charging one of them to full,
          then charge the other one. BAT0 is probably selected if
          both batteries are present}*/

    CHARGE_LEAPFROG, /*
       -if one battery was charging, inhibit the other for 1 minute,
         unless the charging battery has rem_percent that
         is greater than the other by an amount greater than the threshold.
         in that case, inhibit the currently charging battery for 1 minute
       -otherwise, inhibit the battery with a larger rem_percent for
         1 minute */

    CHARGE_CHASING, /*
       -inhibit the batter with a higher rem_percent,
         uninhibit the other*/

    CHARGE_BRACKETS /*
       -for each bracket {sorted lowest-first}:
         -charge the preferred battery until its at or above the bracket
         -charge the other battery until its at or above the bracket
       -if both batteries are above the top bracket, dont inhibit charge*/
};



static void
initialize_prefs (PanelApplet *applet)
{
  panel_applet_add_preferences (PANEL_APPLET (applet),
    "/schemas/apps/tpbattstat-applet/prefs", NULL);

}



           
        /* Preferences */
        if (applet->prefs)
                g_object_unref (applet->prefs);
        
        prefs_key = panel_applet_get_preferences_key (PANEL_APPLET (applet));
        applet->prefs = cpufreq_prefs_new (prefs_key);
        g_free (prefs_key);

	g_signal_connect (G_OBJECT (applet->prefs),
			  "notify::cpu",
			  G_CALLBACK (cpufreq_applet_prefs_cpu_changed),
			  (gpointer) applet);
        g_signal_connect (G_OBJECT (applet->prefs),
                          "notify::show-mode",
                          G_CALLBACK (cpufreq_applet_prefs_show_mode_changed),
                          (gpointer) applet);
        g_signal_connect (G_OBJECT (applet->prefs),
                          "notify::show-text-mode",
                          G_CALLBACK (cpufreq_applet_prefs_show_mode_changed),
                          (gpointer) applet);


