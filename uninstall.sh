#!/bin/sh

NAME=tpbattstat-applet
LIB_INSTALL_DIR=/usr/lib/$NAME
ICON_DIR=/usr/share/pixmaps
SERVER_DIR=/usr/lib/bonobo/servers

sudo rm -rf $LIB_INSTALL_DIR
sudo rm -rf $ICON_DIR/$NAME

sudo ./smapi-battaccess/uninstall-smapi-battaccess.sh

gconftool-2 --recursive-unset /apps/tpbattstat_applet
gconftool-2 --recursive-unset /schemas/apps/tpbattstat_applet

sudo rm $SERVER_DIR/TPBattStatApplet_Factory.server
