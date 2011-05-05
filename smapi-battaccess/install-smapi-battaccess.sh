#!/bin/sh
NAME=smapi-battaccess
BIN_DIR=/usr/bin
APPARMOR_DIR=/etc/apparmor.d

echo compiling $NAME.c to $NAME
gcc $NAME.c -o $NAME
echo install $NAME to $BIN_DIR
cp $NAME $BIN_DIR
echo remove binary
rm $NAME
echo making $NAME have setuid, i.e.: chmod u+s
chmod u+s $BIN_DIR/$NAME

#e.g.: usr.bin.smapi-battaccess
APPARMOR_PROFILE=`echo $BIN_DIR/$NAME | sed 's/^\///' | sed 's/\//./g'`
echo installing apparmor profile $APPARMOR_DIR/$APPARMOR_PROFILE
cp $NAME.apparmor $APPARMOR_DIR/$APPARMOR_PROFILE
