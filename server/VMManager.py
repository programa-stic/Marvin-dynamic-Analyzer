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


#!/usr/bin/env python
import SimpleHTTPServer
import SocketServer
import logging
from DBManager_django import DBManager_django
import Utils
import thread
import traceback
import xml.etree.ElementTree as ET
import json
import settings
import random


class VMManager(object):
    __vmm = None

    def __init__(self):
        self.db = DBManager_django()
        self.running_emulators = set()

    @staticmethod
    def get_vmm():
        if not VMManager.__vmm:
            VMManager.__vmm = VMManager()
        return VMManager.__vmm

    def restore_vm(self, ip):
        thread.start_new_thread(self.one_restore_vm, (ip,))

    def one_restore_vm(self, ip):
        self.restore_host_to_snapshot(self.get_vm_id_from_ip(ip))

    def get_vm_id_from_ip(self, ip):
        xml_response = Utils.run_get_output(
            'java -jar ONE-API/network_info.jar %s %s %s' % (settings.ONE_CREDS, settings.ONE_IP, settings.NET_ID))
        et = ET.fromstring(xml_response)
        for lease in et.iter("LEASE"):
            if lease.find("IP") is not None and lease.find("IP").text == ip:
                return int(lease.find("VM").text)
        raise Exception("NO VM ID found for %s" % ip)

    def restore_host_to_snapshot(self, vm_emulator_id):
        # hardcoding snapshot ID to 1
        return Utils.run_get_output(
            'java -jar ONE-API/restore.jar %s %s %d %d' % (settings.ONE_CREDS, settings.ONE_IP, vm_emulator_id, 0))

    def save_report(self, vm_client_id, content):
        print content
        status = content['status']
        extras = content['description']
        if status == 'SUCCESS':
            self.db.update_success(vm_client_id, extras)
        else:
            # there was an error in the report
            self.db.log_failure(vm_client_id, status, extras)

    def find_target_for_VM_client(self,vm_client_id):
        return self.db.pick_dynamic_test_with_status_unknown(vm_client_id)

    def add_running_emulator(self, emulator):
        self.running_emulators.add(emulator)

    def remove_running_emulator(self, emulator):
        self.running_emulators.remove(emulator)

    def find_emulator_for(self, vulnerability_type):
        possibleEmulators = settings.ANDROID_VM_POOL
        if "SSL" in vulnerability_type:
            key = "SSL"
        elif vulnerability_type in ["PHONEGAP_JS_INJECTION", "JAVASCRIPTINTERFACE"]:
            key = "JAVASCRIPTINTERFACE"
        else:
            key = "NONSSL"
        print set(possibleEmulators[key]) - self.running_emulators
        return random.sample(set(possibleEmulators[key]) - self.running_emulators, 1)[0]

    def get_VMManager_request_handler(self):
        return VMManagerRequestHandler


class VMManagerRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def end_headers(self, filter, apk, download_url):
        # set extra headers for apk
        self.send_header('Content-Type', 'application/json')
        # set to "dummy" for testing
        self.send_header("filter", filter)
        self.send_header("apk", apk)
        self.send_header("download_url", download_url)
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        logging.warning("======= GET STARTED =======")
        if self.path.startswith('/apk'):
            vmm = VMManager.get_vmm()
            vm_client_id = self.client_address[0]
            filter, apk, download_url, description = vmm.find_target_for_VM_client(vm_client_id)
            description['emulator'] = vmm.find_emulator_for(filter)
            vmm.add_running_emulator(description['emulator'])
            description = json.dumps(description)
            self.send_response(200)
            self.end_headers(filter, apk, download_url)
            self.wfile.write(description)
        else:
            self.send_response(404)

    def do_POST(self):
        logging.warning("======= POST STARTED =======")
        try:
            length = int(self.headers['Content-Length'])
            if self.path == '/report' or self.path == '/error':
                content = json.loads(self.rfile.read(length).decode('utf-8'))
                # TODO: should be an asynchrous request so the do_POST doesn't get hang waiting
                # VM ID matchs the vm ip for now
                vm_emulator_id = content['emulator']
                vm_client_id = self.client_address[0]
                vmm = VMManager.get_vmm()
                vmm.remove_running_emulator(vm_emulator_id)
                vmm.save_report(vm_client_id, content)
                vmm.restore_vm(vm_emulator_id)
            self.send_response(200)
        except:
            print traceback.format_exc()
            # if server failed, still restore VM ?
            VMManager.get_vmm().restore_vm(vm_emulator_id)
            self.send_response(500)


def start_VMManager():
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(('0.0.0.0', 8082), VMManager.get_vmm().get_VMManager_request_handler())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.socket.close()


if __name__ == '__main__':
    start_VMManager()
