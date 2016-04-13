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


import os
import sys
import json
import abc
import traceback
import threading
sys.path.append(os.getcwd())
import Utils
from Dispatcher import *
from StorageAnalyzer import StorageAnalyzer
from Emulator import Emulator
from libmproxy import controller, proxy
from libmproxy.proxy.server import ProxyServer
from libmproxy.flow import FlowWriter

class Analyzer(controller.Master):
    acting_component = None

    def __init__(self, filter_id, package_name, description):
        self.report = {}
        self.filter_id = filter_id
        self.package_name = package_name
        self.description = description
        config = proxy.ProxyConfig(port=8080,mode="transparent")
        server = ProxyServer(config)
        controller.Master.__init__(self, server)
        flow_dump_file = open(self.get_package_name()+"_network_traffic", "wb")
        self.network_flow = FlowWriter(flow_dump_file)
        self.should_exit = None
        self.extra_analyzers = [InsecureTransmissionAnalyzer(self),ZIPPathTraversalAnalyzer(self)]

    def get_extra_analyzers(self):
        return self.extra_analyzers

    def get_package_name(self):
        return self.package_name

    def get_filter_id(self):
        return self.filter_id

    def get_description(self):
        return self.description

    def start_analyzer(self, error_message_queue, signal_init, signal_close):
        try:
            signal_init.set()
            self.should_exit = signal_close
            controller.Master.run(self)
            StorageAnalyzer(self).analyze_storage()
            self.send_report()
        except Exception:
            print traceback.format_exc()
            error_message_queue.put(traceback.format_exc())
        finally:
            self.shutdown()

    @staticmethod
    def get_analyzer():
        if not Analyzer.acting_component:
            raise Exception("Analyzer not initialized")
        return Analyzer.acting_component


    @staticmethod
    def get_analyzer_for(filter_id, package_name, description):
        if not Analyzer.acting_component:
            analyzer_class = Dispatcher.get_component_for(filter_id, Analyzer)
            Analyzer.acting_component =  analyzer_class(filter_id, package_name, description)
        return Analyzer.acting_component

    @staticmethod
    def is_for(FILTER_ID):
        return False

    def add_to_report(self, key, value):
        self.report[key] = value

    def get_report(self):
        return self.report

    def handle_request(self, flow):
        for analyzer in self.get_extra_analyzers():
            analyzer.handle_request(flow)
        self.network_flow.add(flow)
        flow.reply()

    def handle_response(self, flow):
        for analyzer in self.get_extra_analyzers():
            try:
                analyzer.handle_response(flow)
            except Exception:
                print traceback.format_exc()
        self.network_flow.add(flow)
        flow.reply()

    def send_report(self):
        Utils.notify(Utils.get_reporter(), 'analyzer', Analyzer.get_analyzer().get_report())


from CommonComponent.ZIPPathTraversalAnalyzer import ZIPPathTraversalAnalyzer
from CommonComponent.InsecureTransmissionAnalyzer import InsecureTransmissionAnalyzer
from DummyFilter.DummyAnalyzer import *
from SSLFilter.SSLAnalyzer import *
from PhonegapFilter.PhonegapAnalyzerJSInjection import *
from PhonegapFilter.PhonegapAnalyzerCVE3500 import *
from FileSchemeFilter.FileSchemeAnalyzer import *
from JavascriptInterfaceFilter.JavascriptInterfaceAnalyzer import *


