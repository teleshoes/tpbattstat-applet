#!/bin/sh

NAME=tpbattstat-applet
LIB_INSTALL_DIR=/usr/lib/$NAME
ICON_DIR=/usr/share/pixmaps
SERVER_DIR=/usr/lib/bonobo/servers

sudo cp tpacpi-bat $LIB_INSTALL_DIR
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

echo installing gconf schemas
echo
gconftool-2 --install-schema-file tpbattstat-applet.schemas

echo applying schemas to the default key dir {not-in-gnome-panel}
PREFS_DIR=/apps/tpbattstat_applet/prefs
SCHEMA_DIR=/schemas$PREFS_DIR
SCHEMAS=`gconftool-2 -a $SCHEMA_DIR | \
         sed 's/^ \([a-zA-Z0-9_]\+\) = .*$/\1/'`
for s in $SCHEMAS; do
  gconftool-2 --apply-schema $SCHEMA_DIR/$s $PREFS_DIR/$s
done

echo installing bonobo server
echo
sudo cp TPBattStatApplet_Factory.server $SERVER_DIR
