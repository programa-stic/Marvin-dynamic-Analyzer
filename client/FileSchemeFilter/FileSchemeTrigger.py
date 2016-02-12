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


import time
import base64
from Trigger import Trigger

THROTTLE = 1000
EVENTS_PER_TEST = 500


class FileSchemeTrigger(Trigger):
    @staticmethod
    def is_for(filter_id):
        # attend Dummy
        return "WEBVIEW_FILE_SCHEME" == filter_id


    def get_exported_activity(self):
        return self.get_description()["activity"]

    # overrides
    def trigger(self):
        html = '''
            <HTML>
               <HEAD>
                  <TITLE>
                     Webview File Scheme Test
                  </TITLE>
               </HEAD>
            <BODY>
            <script>
            var request = new XMLHttpRequest();
            request.open("GET", "http://www.fundacionsadosky.org.ar/?vulnerable_file_scheme=true&activity=''' + base64.b64encode(
            self.get_exported_activity()) + '''", true);
            request.onreadystatechange = function() {
            }
            request.send();
            </script>
               <H1> Webview File Scheme Test</H1>
            </BODY>
            </HTML>
           '''
        with open("test.html", "w") as local:
            local.write(html)
        self.get_emulator().run_adb_command('push test.html /mnt/sdcard/test.html')
        self.get_emulator().run_adb_command(
            "shell am start -n {0}/{1} file://mnt/sdcard/test.html".format(
                self.get_package_name(), self.get_exported_activity()))
        time.sleep(4)
        print "shell am start -n {0}/{1} file://mnt/sdcard/test.html".format(
            self.get_package_name(), self.get_exported_activity())
        self.get_emulator().run_adb_command(
            "shell am start -a android.intent.action.VIEW -a android.intent.category.BROWSEABLE -n {0}/{1} \"file://mnt/sdcard/test.html\"".format(
                self.get_package_name(), self.get_exported_activity()))
        # TODO: how to wait for app trying to load?
        time.sleep(4)