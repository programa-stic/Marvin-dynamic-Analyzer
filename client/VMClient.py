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


# -*- coding: utf-8 -*-
import time
import Utils
import urllib
import urllib2
import traceback
import sys
import json
import multiprocessing
from Reporter import Reporter
from Trigger import Trigger
from Analyzer import Analyzer
from Emulator import Emulator
import Queue
import threading


class VMClient(object):
    # since it's not thread safe, no modification of VMClient should occur during running of Trigger or Reporter
    vm_client = None

    @classmethod
    def get_VM_client(cls):
        if cls.vm_client is None:
            cls.vm_client = VMClient()
        return cls.vm_client

    def __init__(self):
        self.get_apk_from_manager()
        self.trigger = Trigger.get_trigger_for(self.get_filter_tag(), self.get_package_name(), self.get_description())
        self.reporter = Reporter.get_reporter_for(self.get_filter_tag(), self.get_package_name(),
            self.get_description())
        self.analyzer = Analyzer.get_analyzer_for(self.get_filter_tag(), self.get_package_name(),
            self.get_description())
        self.emulator = Emulator.get_emulator_for(self.get_filter_tag(), self.get_package_name(),
            self.get_description())
        self.error_queue = multiprocessing.Queue()
        self.setup_device()

    def get_emulator(self):
        return self.emulator

    def get_package_name(self):
        return self.package_name

    def get_filter_tag(self):
        return self.filter_id

    def get_description(self):
        return self.description

    def get_apk_from_manager(self):
        if Utils.isTestingMode():
            print "VMClient is being tested"
            self.filter_id = sys.argv[1]
            self.package_name = sys.argv[2]
            self.description = json.loads(sys.argv[3])
        else:
            url = '''http://''' + Utils.get_VM_Manager() + '/apk'
            # Open the url
            try:
                response = urllib.urlopen(url)
                self.filter_id = response.info().dict['filter']
                self.package_name = response.info().dict['apk']  # save only name
                download_url = response.info().dict['download_url']  # save only name
                content = response.read()
                self.description = json.loads(content)
                response = urllib.urlopen(download_url)
                # Open our local file for writing
                with open(self.package_name + ".apk", "w") as local_file:
                    local_file.write(response.read())
                    local_file.flush()
                    local_file.close()
                # handle errors
                print "HANDLING:"
                print "VULNERABILITY: " + self.filter_id
                print "PACKAGE: " + self.package_name
                print "DESCRIPTION: " + json.dumps(self.description)
            except urllib2.HTTPError, e:
                print "HTTP Error:", e.code, url
            except urllib2.URLError, e:
                print "URL Error:", e.reason, url

    def send_FAIL_signal(self,description):
        headers = {'status': 'ERROR', 'emulator': self.get_emulator().get_remote_ip(),
                   'description': description}
        Utils.notify(Utils.get_VM_Manager(), 'error', headers)

    def setup_device(self):
        emulator = self.get_emulator()
        # install application
        (output, err) = emulator.run_adb_command('install -r %s' % (self.package_name + ".apk"))
        self.add_error_message(output)
        self.add_error_message(err)
        #set client as gateway so analyzer intercepts traffic
        self.emulator.set_localhost_as_gateway()


    def start_trigger_process(self):
        return self.start_component_and_wait_for_initialization(self.trigger.start_trigger)

    def start_analyzer_process(self):
        return self.start_component_and_wait_for_initialization(self.analyzer.start_analyzer)

    def start_reporter_process(self):
        return self.start_component_and_wait_for_initialization(self.reporter.start_reporter)

    def start_component_and_wait_for_initialization(self, target):
        signal_init = multiprocessing.Event()
        signal_close = multiprocessing.Event()
        process = multiprocessing.Process(target=target, args=(self.error_queue, signal_init, signal_close))
        process.start()
        # wait for initialization
        signal_init.wait()
        return (process, signal_close)

    def wait_for_component(self, component):
        component[1].set()
        component[0].join()

    def time_out(self):
        print "A time out has occurred, the analysis failed"
        self.add_error_message("THE TEST TIMED OUT")
        self.send_errors()

    def add_error_message(self, message):
        self.error_queue.put(message)

    def send_errors(self):
        errors = []
        while True:
            try:
                errors.append(self.error_queue.get_nowait())
            except Queue.Empty:
                break
        self.send_FAIL_signal({"errors": errors})

    def start_timeout_error_handler(self):
        self.timer = threading.Timer(300, self.time_out)
        self.timer.start()

    def finish_timeout_error_handler(self):
        self.timer.cancel()

    def get_max_tries(self):
        return 1000

    def start_components(self):
        try:
            self.start_timeout_error_handler()
            if int(self.get_description()['count']) > self.get_max_tries():
                self.send_FAIL_signal({'tries': 'Couldn\'t verify the vulnerability dinamically'})
            else:
                analyzer = self.start_analyzer_process()
                reporter = self.start_reporter_process()
                # waits for reporter and analyzer to start before trigger.
                trigger = self.start_trigger_process()
                # wait trigger process to finish
                self.wait_for_component(trigger)
                print "already closed trigger"
                # signal end of trigger
                self.wait_for_component(analyzer)
                print "already closed analyzer"
                self.wait_for_component(reporter)
                print "already closed reporter"
            self.finish_timeout_error_handler()
        except:
            self.error_queue.put(traceback.format_exc())
            self.send_errors()
        finally:
            self.emulator.disconnect()


if __name__ == '__main__':
    VMClient.get_VM_client().start_components()
