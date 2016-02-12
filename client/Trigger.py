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
import traceback
from Dispatcher import *
from Emulator import Emulator
# Import Filters after defining trigger

class Trigger(object):
    # only need one component
    acting_component = None

    def __init__(self, filter_id, package_name, description):
        self.report = {}
        self.filter_id = filter_id
        self.package_name = package_name
        self.description = description

    def get_package_name(self):
        return self.package_name

    def get_filter_id(self):
        return self.filter_id

    def get_description(self):
        return self.description

    def get_emulator(self):
        return Emulator.get_emulator()

    @staticmethod
    def get_trigger():
        if not Trigger.acting_component:
            raise Exception("Trigger not initialized")
        return Trigger.acting_component

    @staticmethod
    def get_trigger_for(filter_id, package_name, description):
        if not Trigger.acting_component:
            trigger_class = Dispatcher.get_component_for(filter_id, Trigger)
            Trigger.acting_component = trigger_class(filter_id, package_name, description)
        return Trigger.acting_component

    @staticmethod
    # returns if its for FILTER_ID
    def is_for(FILTER_ID):
        return False

    @abc.abstractmethod
    def trigger(self):
        print "Trigger Base class"

    def add_to_report(self, key, value):
        if self.report[key]:
            self.report[key] = value
        else:
            self.report[key].append(value)

    def get_report(self):
        return self.report

    def send_report(self):
        Utils.notify(Utils.get_reporter(), 'trigger', self.get_report())

    def start_trigger(self, error_message_queue, signal_init, signal_close):
        try:
            # do not block VMclient
            signal_init.set()
            self.trigger()
            self.send_report()
        except Exception:
            print traceback.format_exc()
            error_message_queue.put(traceback.format_exc())


from DummyFilter.DummyTrigger import *
from SSLFilter.SSLTrigger import *
from PhonegapFilter.PhonegapTriggerJSInjection import *
from PhonegapFilter.PhonegapTriggerCVE3500 import *
from FileSchemeFilter.FileSchemeTrigger import *
from JavascriptInterfaceFilter.JavascriptInterfaceTrigger import *


