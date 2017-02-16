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


from Analyzer import Analyzer
from libmproxy.protocol.http import decoded
import lxml.html
import base64
import sys


class JavascriptInterfaceAnalyzer(Analyzer):

    @staticmethod
    def is_for(filter_id):
        # attend Dummy
        return "JAVASCRIPTINTERFACE" == filter_id

    def handle_request(self, flow):
        if flow.request.path.find("?vulnerable_javascript_injection") != -1:
            visited_url_index = flow.request.path.find("&url=")
            interface_url_index = flow.request.path.find("&interface=")
            self.add_to_report(self.get_filter_id(),
                               "Dynamically verified that malicious Javascript can be injected via HTTP via url %s and can run arbitrary code via the Javascript Interface %s" % (
                                   base64.b64decode(
                                       flow.request.path[visited_url_index + len("&url="):]),
                                   flow.request.path[interface_url_index + len("&interface="):visited_url_index]))
        Analyzer.handle_request(self,flow)

    def handle_response(self, flow):
        print "request path is %s " % flow.request.path
        # If it's injectable and it's not the injected request
        requested_site = flow.request.headers["Host"][0]
        if flow.request.scheme.endswith("http") and requested_site.find("www.fundacionsadosky.org.ar") == -1:
            visited_url = base64.b64encode(requested_site + flow.request.path)
            #taken from www.droidsec.org/tests/addjsif/
            script = '''vulnerable=[];for(i in top){el=top[i];if(el==null){continue};if(typeof(el)==='function'){continue}try{top[i].getClass().forName('java.lang.Runtime');vulnerable.push(i)}catch(e){}}if(vulnerable.length>0){var request=new XMLHttpRequest();request.open("GET","http://www.fundacionsadosky.org.ar/?vulnerable_javascript_injection=true&interface="+vulnerable.join()+"&url=''' + visited_url + '''",true);request.onreadystatechange=function(){};request.send()}'''
            content_type = flow.response.headers.get("Content-Type")
            if not content_type:
               content_type = flow.response.headers.get("Content-type")
            if content_type and "text/html" in content_type[0]:
                with decoded(flow.response):  # automatically decode gzipped responses.
                    if flow.response.content:
                        try:
                            response = flow.response.content
                            print "Response is "+response
                            root = lxml.html.fromstring(response)
                            if root.find('.//*') is not None:
                                print  "TRIED MODIFYING /html " + requested_site+ flow.request.path
                                # is HTML, use lxml to insert to head, body or script
                                append_in = root.find('.//head')
                                if append_in is None:
                                    append_in = root.find('.//body')
                                elif append_in is None:
                                    append_in = root.find('.//script').getparent()
                                else:
                                    append_in = root
                                script = lxml.html.fromstring('<script>' + script + '</script>')
                                if append_in is not None:
                                    append_in.append(script)
                                    flow.response.content = lxml.html.tostring(root)
                        except:
                            print "There was a problem parsing the html response, skip it"
                            # mimetype may be application/javascript or text/javascript
            elif content_type and "javascript" in content_type[0]:
                with decoded(flow.response):  # automatically decode gzipped responses.
                    print  "TRIED MODIFYING /javascript " + requested_site + flow.request.path
                    # is searching for library .JS (both cases sensitive) or JQUERY
                    flow.response.content = script.encode("utf-8") + flow.response.content
        Analyzer.handle_response(self,flow)
