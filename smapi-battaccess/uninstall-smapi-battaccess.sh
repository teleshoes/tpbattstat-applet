#!/bin/sh
SMAPI_BA=smapi-battaccess
BIN_DIR=/usr/bin
APPARMOR_DIR=/etc/apparmor.d
APPARMOR_PROFILE=`echo $BIN_DIR/$SMAPI_BA | sed 's/^\///' | sed 's/\//./g'`

rm $BIN_DIR/$SMAPI_BA
rm $APPARMOR_DIR/$APPARMOR_PROFILE
