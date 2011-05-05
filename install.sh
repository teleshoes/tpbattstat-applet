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
sudo cp $NAME $BIN_DIR

echo compiling and installing smapi-battaccess
sudo ./smapi-battaccess/install-smapi-battaccess.sh

