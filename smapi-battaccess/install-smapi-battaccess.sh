#!/bin/sh
SMAPI_BA=smapi-battaccess
BIN_DIR=/usr/bin
APPARMOR_DIR=/etc/apparmor.d
APPARMOR_PROFILE=`echo $BIN_DIR/$SMAPI_BA | sed 's/^\///' | sed 's/\//./g'`

echo compiling $SMAPI_BA.c to $SMAPI_BA
echo
gcc $SMAPI_BA.c -o $SMAPI_BA

echo install $SMAPI_BA to $BIN_DIR
echo
rm -f $BIN_DIR/$SMAPI_BA
cp $SMAPI_BA $BIN_DIR

echo remove binary
echo
rm $SMAPI_BA

echo making $SMAPI_BA have setuid, i.e.: chmod u+s
echo
chmod u+s $BIN_DIR/$SMAPI_BA

echo installing apparmor profile $APPARMOR_DIR/$APPARMOR_PROFILE
cp $SMAPI_BA.apparmor $APPARMOR_DIR/$APPARMOR_PROFILE
