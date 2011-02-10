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

#ifndef TPBATTSTAT_BATTINFO_H
#define TPBATTSTAT_BATTINFO_H

#include "tpbattstat-prefs.h"

enum BatteryState { IDLE, CHARGING, DISCHARGING };

typedef struct {
    int id;
    int installed;
    int force_discharge;
    int inhibit_charge_minutes;
    int remaining_percent;
    int power_avg;
    int remaining_capacity;
    int last_full_capacity;
    int design_capacity;
    enum BatteryState state;
} Battery;

typedef struct {
    int ac_connected;
    Battery *bat0;
    Battery *bat1;
    char *msg;
    unsigned long count;
} BatteryStatus;

void get_battery_status(BatteryStatus* status);

int perhaps_force_discharge(BatteryStatus *status,
        enum DischargeStrategy strategy, int threshold);

int perhaps_inhibit_charge(BatteryStatus *status,
        enum ChargeStrategy strategy, int threshold,
        const int brackets[], int bracketsSize, int bracketsPrefBat);

#endif /* TPBATTSTAT_BATTINFO_H */
