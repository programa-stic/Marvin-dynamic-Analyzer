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


import abc
import time
import Utils
import netifaces
import logging

class Emulator(object):
    acting_component = None

    def __init__(self, filter_id, package_name, description):
        self.remote_ip = description['emulator'] + ':5556'
        Utils.run_blocking_cmd("adb connect {0}:5556".format(self.remote_ip))
        Utils.run_blocking_cmd("adb root")
        logging.debug("waiting to connect to adb as root")
        time.sleep(5)
        Utils.run_blocking_cmd("adb connect {0}:5556".format(self.remote_ip))
        logging.debug("connected to adb as root")

    @staticmethod
    def get_emulator_for(filter_id, package_name, description):
        if not Emulator.acting_component:
            Emulator.acting_component = Emulator(filter_id, package_name, description)
        return Emulator.acting_component

    @staticmethod
    def get_emulator():
        return Emulator.acting_component

    def set_localhost_as_gateway(self):
        local_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
        return self.run_adb_command('shell \"busybox route delete default; route add default gw {0} dev eth0\"'.format(local_address))

    def disconnect(self):
        return Utils.run_blocking_cmd("adb disconnect")

    def get_remote_ip(self):
        return self.remote_ip.split(":")[0]

    def run_adb_command(self, command):
        return Utils.run_blocking_cmd("adb -s {0} ".format(self.remote_ip) + command)
