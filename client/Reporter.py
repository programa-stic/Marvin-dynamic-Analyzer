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


import SimpleHTTPServer
import SocketServer
import os
import abc
import sys
import logging
import traceback
import json
import threading
import multiprocessing
from Dispatcher import *
from Emulator import Emulator


class ReporterHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    report = {}

    def is_full_report(self):
        return len(ReporterHandler.report.keys()) == 2

        # only has POST

    def do_POST(self):
        # logging.warning("======= POST STARTED =======")
        try:
            if self.path == '/trigger' or self.path == '/analyzer':
                length = int(self.headers['Content-Length'])
                content = json.loads(self.rfile.read(length).decode('utf-8'))
                #save any of those two reports
                ReporterHandler.report[self.path[1:]] = content
                logging.warning(ReporterHandler.report)
                if self.is_full_report():  #have both reports already
                    Reporter.get_reporter().send_report(ReporterHandler.report['trigger'],
                                                        ReporterHandler.report['analyzer'])
                self.send_response(200)
            else:
                self.send_response(404)
                return
        except:
            logging.warning(traceback.format_exc())
            self.send_response(500)


class Reporter(object):
    acting_component = None

    def __init__(self, filter_id, package_name, description):
        self.filter_id = filter_id
        self.package_name = package_name
        self.description = description

    @staticmethod
    def get_reporter():
        if not Reporter.acting_component:
            raise Exception("Reporter not initialized")
        return Reporter.acting_component

    @staticmethod
    def get_reporter_for(filter_id, package_name, description):
        if not Reporter.acting_component:
            reporter_class = Dispatcher.get_component_for(filter_id, Reporter)
            Reporter.acting_component = reporter_class(filter_id, package_name, description)
        return Reporter.acting_component

    @staticmethod
    # returns if its for FILTER_ID
    def is_for(filter_id):
        return False

    def get_package_name(self):
        return self.package_name

    def get_filter_id(self):
        return self.filter_id

    def get_description(self):
        return self.description

    def start_reporter(self, error_message_queue,signal_init,signal_close):
        try:
           Handler = ReporterHandler
           SocketServer.TCPServer.allow_reuse_address = True
           server = SocketServer.TCPServer(('localhost', 8081), Handler)
           server_thread = threading.Thread(target=server.serve_forever,args=())
           server_thread.start()
           signal_init.set()
           signal_close.wait()
           server.shutdown()
        except Exception:
           print traceback.format_exc()
           error_message_queue.put(traceback.format_exc())

    @abc.abstractmethod
    def create_vm_reports(self, trigger_rep, analyzer_rep):
        # create final report to send VM Manager
        ip = Emulator.get_emulator().get_remote_ip()
        return {'status': 'ERROR', 'emulator': ip, 'description': {'errors': 'Called abstract method from reporter'}}

    def send_report(self, trigger, analyzer):
        filter_report = self.create_vm_reports(trigger, analyzer)
        ip = Emulator.get_emulator().get_remote_ip()
        filter_report['emulator'] = ip
        if Utils.isTestingMode():
            print "FINAL REPORT "
            print filter_report
        else:
            Utils.notify(Utils.get_VM_Manager(), 'report', filter_report)


from DummyFilter.DummyReporter import *
from SSLFilter.SSLReporter import *
from FileSchemeFilter.FileSchemeReporter import *
from PhonegapFilter.PhonegapReporter import *
from JavascriptInterfaceFilter.JavascriptInterfaceReporter import *

