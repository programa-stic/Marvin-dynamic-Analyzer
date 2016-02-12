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


import urllib2
import subprocess
import shlex
import traceback
import json
import settings

def isTestingMode():
    return settings.DEBUG_MODE


def notify(address, path, params):
    data = json.dumps(params)
    url = '''http://''' + address + '/' + path
    try:
        request = urllib2.Request(url, data=data, headers={'Content-Type': 'application/json'})
        return urllib2.urlopen(request).read()
    except:
        print traceback.format_exc()
        pass


def run_non_blocking_cmd(command):
    return subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def log_process(p):
    if not p:
        return "process is null"
    s = None
    if p.poll() is not None:
        s = "process has finished already. Return code: %s\n" % p.returncode
    else:
        s = "process hasn't finished. Terminating it."
        p.kill()
    o, e = p.communicate()
    s += "STDOUT: %s, STDERR : %s " % (o, e)
    return s


def run_blocking_cmd(command):
    return subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


def get_subclasses(c):
    subclasses = c.__subclasses__()
    for d in list(subclasses):
        subclasses.extend(get_subclasses(d))
    return subclasses


def get_VM_Manager():
    return settings.VM_MANAGER_IP


def get_reporter():
    return settings.REPORTER_IP
