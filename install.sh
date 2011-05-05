#!/bin/sh

NAME=tpbattstat-applet
BIN_DIR=/usr/bin
ICON_DIR=/usr/share/pixmaps
SERVER_DIR=/usr/lib/bonobo/servers

cd src
echo copying $NAME.py to $BIN_DIR
echo
sudo cp $NAME.py $BIN_DIR
cd ../

cd smapi-battaccess
echo compiling and installing smapi-battaccess
echo
sudo ./install-smapi-battaccess.sh
cd ../

cd icons
echo copying icons
echo
sudo rm -rf $ICON_DIR/$NAME/
sudo mkdir $ICON_DIR/$NAME/
sudo cp -ar * $ICON_DIR/$NAME/
cd ../

echo installing gconf schemas
echo
gconftool-2 --install-schema-file tpbattstat-applet.schemas

echo installing bonobo server
echo
sudo cp TPBattStatApplet_Factory.server $SERVER_DIR
