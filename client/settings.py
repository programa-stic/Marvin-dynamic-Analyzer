# Copyright (c) 2015, Fundacion Dr. Manuel Sadosky
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


VM_MANAGER_IP = '172.30.0.8:8082'
REPORTER_IP = 'localhost:8081'
DEBUG_MODE = False
FUZZER_VALUES={
    'PASSWORD': 's3cr3tpass',
    'MAIL' : 'fakeemailandroid@gmail.com',
    'PHONE' : '1112341234',
    'CONTACTNAME' :  'C0ntactFuzz',
    'CONTACTPHONE' : '1107060504'
}
FUZZER_PRIVACY_VALUES={
	"android.telephony.TelephonyManager" : {
	"getSimOperatorName" : "QUAM-SIM",
	"getSimOperator" : "72201",
	"getNetworkOperatorName" : "QUAM-NETWORK",
	"getNetworkOperator" : "72207"
},
"com.android.internal.telephony.gsm.GSMPhone" : {
	"getDeviceId" : "352738061926670",
	"getImei" : "352738061926671",
	"getSubscriberId" : "722010000906017",
	"getLine1Number" : "1112341234"
},

"com.android.internal.telephony.gsm.CDMAPhone" : {
	"getDeviceId" : "352738061926672",
	"getMeid" : "352738061926673",
	"getSubscriberId" : "722010000906017",
	"getLine1Number" : "541101010101"
},
"com.android.internal.telephony.PhoneBase" :
{
	"getIccSerialNumber" : "8954010111009060172f"

},
"android.net.wifi.WifiInfo" : {
	"getBSSID" : "de:ad:be:ef:aa:aa",
	"getIpAddress" : "192.168.0.2",
	"getMacAddress" : "de:ad:be:ef:bb:bb",
	"getSSID" : "ThizIsMyWifi"
},

"com.android.settings.Utils" : {
	"getWifiIpAddresses" : "192.168.0.2",
	"getDefaultIpAddresses" : "192.168.0.2"
},
"android.location.LocationManager" : {
	"requestLocationUpdates" : "-34.603773, -58.381700",
	"getLastKnownLocation" : "-34.603773, -58.381700"
},
"android.net.wifi.WifiManager" : {
	"getConfiguredNetworks" : "Not applicable yet",
	"getScanResults" : "Not applicable yet"
}
}