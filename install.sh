#!/bin/sh

NAME=tpbattstat-applet
BIN_DIR=/usr/bin
ICON_DIR=/usr/share/pixmaps

DEPS=libpanelapplet-2.0
CFLAGS=`pkg-config --cflags $DEPS`
LIBS=`pkg-config --libs $DEPS`

cd src
for srcfile in `ls *.c`; do
  echo compiling $srcfile to object
  echo
  gcc $CFLAGS $LIBS -g -O2 -c $srcfile
done

echo compiling $NAME from objects
echo
gcc -g -O2 -o $NAME *.o $LIBS

echo installing $NAME to $BIN_DIR
echo
sudo cp $NAME $BIN_DIR

echo compiling and installing smapi-battaccess
echo
sudo ./smapi-battaccess/install-smapi-battaccess.sh

echo copying icons
echo
sudo rm -rf $ICON_DIR/$NAME/
sudo mkdir $ICON_DIR/$NAME/
sudo cp -ar icons/* $ICON_DIR/$NAME/

echo installing gconf schemas
echo
gconftool-2 --install-schema-file tpbattstat-applet.schemas

