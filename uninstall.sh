#!/bin/sh

NAME=tpbattstat-applet
BIN_DIR=/usr/bin
ICON_DIR=/usr/share/pixmaps

sudo rm $BIN_DIR/$NAME
sudo rm -rf $ICON_DIR/$NAME

sudo ./smapi-battaccess/uninstall-smapi-battaccess.sh

gconftool-2 --recursive-unset /schemas/apps/tpbattstat_applet

sudo rm $SERVER_DIR TPBattStatApplet_Factory.server
