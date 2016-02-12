#!/bin/sh
clear
echo "-----------------------------"
echo "Root script for Android 4.3"
echo "    By Quinny899 @ XDA"
echo "  Root by Chainfire @ XDA"
echo "-----------------------------"
echo "Script loaded"
echo "Installing to device from device"
echo "Mounting..."
mount -o rw,remount /system
echo "Removing old files..."
rm -r -f /system/bin/.ext
rm -f /system/bin/.ext/.su
rm -f /system/xbin/daemonsu
rm -f /system/xbin/su
#rm -f /system/etc/init.sh
rm -f /system/app/Superuser.apk
echo "Copying files..."
mkdir /system/bin/.ext
cp system/bin/.ext/.su /system/bin/.ext/
cp system/xbin/su /system/xbin/
cp system/xbin/daemonsu /system/xbin/
cp system/app/Superuser.apk /system/app/
cat system/etc/init.sh >> /system/etc/init.sh 
echo "Setting permissions..."
chmod 06755 /system/xbin/su
chmod 06755 /system/xbin/daemonsu
chmod 06755 /system/bin/.ext/.su
chmod 777 /system/bin/.ext
chmod 755 /system/etc/init.sh
echo "Cleaning up..."
echo "Finished. You need to reboot for root to be available"
