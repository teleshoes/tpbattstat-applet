#!/bin/sh

NAME=tpbattstat-applet
LIB_INSTALL_DIR=/usr/lib/$NAME
ICON_DIR=/usr/share/pixmaps

cd src
echo copying $NAME.py to $LIB_INSTALL_DIR
echo
sudo mkdir -p $LIB_INSTALL_DIR
sudo cp *.py $LIB_INSTALL_DIR
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
