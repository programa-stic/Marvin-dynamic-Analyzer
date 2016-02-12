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


import Utils
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'django_support'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_support.settings")
from django.conf import settings
from django.db import connections
from django_support.models import VulnerabilityResult
from django_support.models import App
from django_support.models import DynamicTestResults
from DBCache_django import DBCache_django
import settings
import random

class DBManager_django(object):

	def __init__(self):
		self.cache = DBCache_django()

	def default_filter_state(self, filter_id, apk_name):
		return {"status":"UNKNOWN", "count":0, "description":{}}

	def pick_dynamic_test_with_status_unknown(self,vm_client_id):
		dynamic_test = DynamicTestResults.objects.filter(status__exact='UNKNOWN').order_by('?').first()
		package_name = dynamic_test.vuln.app.package_name
		vulnerability_type = dynamic_test.vuln.name
		if(dynamic_test.vuln.dynamic_test_params is not None):
			dynamic_test_params = json.loads(dynamic_test.vuln.dynamic_test_params)
		else:
			dynamic_test_params = {}
		dynamic_test_params['count'] = dynamic_test.count
		download_url = settings.DOWNLOAD_APK_SITE + '%d'%dynamic_test.vuln.app.id + '/apk/?'
		self.cache.cache_dynamic_test_for_vm(vm_client_id,dynamic_test)
		print (vulnerability_type, package_name, download_url, dynamic_test_params)
		return (vulnerability_type, package_name, download_url, dynamic_test_params)

	def update_success(self,vm_client_id,description):
		dynamic_test = self.cache.get_dynamic_test_for_vm(vm_client_id)
		for vuln_type in description.keys():
			if vuln_type == dynamic_test.vuln.name:
				dynamic_test.status = "SUCCESS"
				dynamic_test.count +=1
				dynamic_test.description = {vuln_type : description[vuln_type]}
				dynamic_test.save()
			else:
				for vulnerability in description[vuln_type]:
					#its one of the dynamic only tested vulnerabilities, create a new vulnerability with its
					#description
					vulnerability = VulnerabilityResult(name = vuln_type,
											 description = vulnerability,
											 confidence = 1,
											 dynamicTest = False,
											 dynamic_test_params = None,
											 app = dynamic_test.vuln.app)
					vulnerability.save()


	def log_failure(self,vm_client_id,status,extras):
		dynamic_test = self.cache.get_dynamic_test_for_vm(vm_client_id)
		dynamic_test.status = status
		dynamic_test.count +=1
		dynamic_test.description = extras
		dynamic_test.save()

