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

#ifndef TPBATTSTAT_PREFS_H
#define TPBATTSTAT_PREFS_H

#include <panel-applet.h>

#define SCHEMA_DIR "/schemas/apps/tpbattstat_applet/prefs"

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

typedef struct {
    int delay;
    enum DischargeStrategy dischargeStrategy;
    int dischargeLeapfrogThreshold;
    enum ChargeStrategy chargeStrategy;
    int chargeLeapfrogThreshold;
    int chargeBracketsPrefBattery;
    int *chargeBrackets;
    int chargeBracketsSize;

    int displayPowerAvg;
    int displayColoredText;
    int displayIcons;
    int displayOnlyOneIcon;
    int displayBlinkingIndicator;
} Prefs;

void load_prefs (PanelApplet *applet, Prefs *prefs);
void initialize_prefs (PanelApplet *applet);

#endif /* TPBATTSTAT_PREFS_H */
