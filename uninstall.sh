#!/bin/sh

NAME=tpbattstat-applet
LIB_INSTALL_DIR=/usr/lib/$NAME
ICON_DIR=/usr/share/pixmaps

sudo rm -rf $LIB_INSTALL_DIR
sudo rm -rf $ICON_DIR/$NAME

sudo ./smapi-battaccess/uninstall-smapi-battaccess.sh
