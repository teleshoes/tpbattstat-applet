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

#include <stdio.h>
#include <stdlib.h>

#define smapi_dir "/sys/devices/platform/smapi"

enum BatteryState { IDLE, CHARGING, DISCHARGING };

int
read_battery_prop(int battery_id, const char *property)
{
    int buflen = 256;
    char *buf = malloc(buflen);

    if(battery_id < 0)
        sprintf(buf, "%s/%s", smapi_dir, property);
    else
        sprintf(buf, "%s/BAT%d/%s", smapi_dir, battery_id, property);

    FILE *f = fopen(buf, "r");
    if(f == NULL){
        buf[0] = '\0';}
    else
    {
        char *str = fgets(buf, buflen, f);
        fclose(f);
        if(str == NULL)
            buf[0] = '\0';
    }
    
    //chomp
    int i;
    for(i=0; i<buflen-1; i++)
    {
        if(buf[i] == '\n' || buf[i] == '\0')
            break;
    }
    buf[i] = '\0';

    int res;
    if(strcmp(property, "state") == 0)
    {
        if(strcmp(buf, "charging") == 0)
            res = CHARGING;
        else if(strcmp(buf, "discharging") == 0)
            res = DISCHARGING;
        else
            res = IDLE;
    }
    else
      res = atoi(buf);
    
    free(buf);
    return res;
}

void
write_battery_prop(int battery_id, const char *property, const char *value)
{
    int buflen = 256;
    char *buf = malloc(buflen);

    if(battery_id < 0)
        sprintf(buf, "%s/%s", smapi_dir, property);
    else
        sprintf(buf, "%s/BAT%d/%s", smapi_dir, battery_id, property);

    FILE *f = fopen(buf, "w");
    if(f != NULL)
    {
        fprintf(f, "%s\n", value);
        fclose(f);
    }
    free(buf);
}

int main( int argc, const char* argv[] )
{
    if((argc < 4) ||
       (argc == 4 && strcmp(argv[1], "-g") != 0) ||
       (argc == 5 && strcmp(argv[1], "-s") != 0) ||
       (argc > 5)
    )
    {
        fprintf(stderr,
          "Usage:\n"
          "  %s -g BATT_ID BATT_PROP\n"
          "  %s -s BATT_ID BATT_PROP VALUE\n",
          argv[0], argv[0]);
        exit(1);
    }

    if(strcmp(argv[1], "-g") == 0)
    {
        int battery = atoi(argv[2]);
        const char *prop = argv[3];
        int val = read_battery_prop(battery, prop);
        printf("%d", val);
    }
    else if(strcmp(argv[1], "-s") == 0)
    {
        int battery = atoi(argv[2]);
        const char *prop = argv[3];
        const char *val = argv[4];
        write_battery_prop(battery, prop, val);
    }
}

