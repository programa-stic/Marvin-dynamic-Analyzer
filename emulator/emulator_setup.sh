#WORKING_FOLDER_PATH=/home/android/Android
echo "Run with {SSL/NOSSL} {EMULATOR-IP} {GATEWAY-IP-FOR-EMULATOR} as args"
WORKING_FOLDER_PATH=emulator_support_files
EMULATOR_TYPE=$1
emulator=$2:5556
GW_FOR_EMULATOR=$3
echo "Using emulator address $emulator"
#Rooting, substrate, installing ssl bypass and fuzzer then linking 
#rooting the emulator 
connect_adb ()
{
adb disconnect
adb connect "$1"
sleep 8
adb -s "$1" root
#wait for adb to restart
sleep 8
adb connect "$1"
}

connect_adb "$emulator"
#disabling lockscreen and suspension
adb -s "$emulator" shell "sqlite3 /data/system/locksettings.db \"UPDATE locksettings SET value = '1' WHERE name = 'lockscreen.disabled'\""
#adb -s "$emulator" shell "sqlite3 /data/data/com.android.providers.settings/databases/settings.db \"update system set value='-1' where name='screen_off_timeout'\""
#rooting emulator
adb -s "$emulator" push $WORKING_FOLDER_PATH/Android-x86-RootScript-4.3/ /data/local/
adb -s "$emulator" shell "cd /data/local; sh install-device.sh"
#add to init.sh remote adb, configure static ip to emulator and remove return 0
adb -s "$emulator" remount
adb -s "$emulator" shell "sed -i 's/return 0//g' /system/etc/init.sh"
adb -s "$emulator" shell "echo 'adb tcpip 5556 &' >> /system/etc/init.sh"
adb -s "$emulator" shell "echo 'ifconfig eth0 $2 netmask 255.255.255.0 &' >> /system/etc/init.sh"
adb -s "$emulator" shell "echo 'busybox route add default gw $GW_FOR_EMULATOR dev eth0 &' >> /system/etc/init.sh"
adb -s "$emulator" shell "echo 'return 0' >> /system/etc/init.sh"
#reboot needed for SuperUser.apk to be instaled
adb -s "$emulator" reboot &
sleep 60
connect_adb "$emulator"
#start supersu to add shared_prefs configuration
adb -s "$emulator" shell "am start -a android.intent.action.MAIN -n eu.chainfire.supersu/.MainActivity"
sleep 8
#change shared_pref to allow all apps
adb -s "$emulator" push $WORKING_FOLDER_PATH/eu.chainfire.supersu_preferences.xml /data/data/eu.chainfire.supersu/shared_prefs/eu.chainfire.supersu_preferences.xml
#reboot needed for grant access to be resolved
adb -s "$emulator" reboot &
sleep 60
connect_adb "$emulator"
#installing cydia  
adb -s "$emulator" install -r $WORKING_FOLDER_PATH/com.saurik.substrate.apk
#installing extensions
#if first emulator, install trust-killer
if [[ "$EMULATOR_TYPE" == *"NOSSL"* ]]
then
  adb -s "$emulator" install -r $WORKING_FOLDER_PATH/Android-SSL-TrustKiller.apk
fi
adb -s "$emulator" install -r $WORKING_FOLDER_PATH/Marvin-toqueton.apk
#linking cydia
adb -s "$emulator" shell /data/data/com.saurik.substrate/lib/libSubstrateRun.so do_link
#rm all sdcard content
adb -s "$emulator" shell "ls -d /sdcard/* | grep -v Android | xargs rm -r"
#open substrate to update permitted.list (wait some seconds)pm 
adb -s "$emulator" shell am start -a android.intent.action.MAIN -n com.saurik.substrate/.SetupActivity
sleep 8
#copy the privacy.json file to sdcard
adb -s "$emulator" shell am start -a android.intent.action.MAIN -n ar.fsadosky.marvintoqueton/.MainActivity
#clear gapps and google play services because of crashes
adb -s "$emulator" shell "pm uninstall com.google.android.gms"
adb -s "$emulator" shell "pm clear com.google.android.gms"
adb -s "$emulator" shell "pm clear com.google.android.gsf"
sleep 8
#rebooting phone
adb -s "$emulator" shell /system/bin/setprop ctl.restart zygote
#Busybox already installed in android-x86, no longer needs installing
connect_adb "$emulator"
