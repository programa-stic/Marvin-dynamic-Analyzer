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


from AnalyzerDecorator import AnalyzerDecorator
import settings


# DummyAnalyzer for testing
class InsecureTransmissionAnalyzer(AnalyzerDecorator):

    def sensitiveValues(self):
        return settings.FUZZER_VALUES

    def privateValues(self):
        merged = {}
        for values in settings.FUZZER_PRIVACY_VALUES.values():
            merged.update(values)
        return merged

    def keywords(self):
        values = self.sensitiveValues()
        values.update(self.privateValues())
        return values

    def requestContains(self, flow, keyword_value):
        inPath =  keyword_value in flow.request.path
        inContent =flow.request.content is not None and keyword_value in flow.request.content
        inHeaders = keyword_value in str(flow.request.headers)
        return inPath or inContent or inHeaders

    def handle_request(self, flow):
        print flow.request.headers["Host"][0]
        if flow.request.scheme.endswith("http"):
            for (key_info, private_info_fuzzer) in self.keywords().iteritems():
                if (self.requestContains(flow,private_info_fuzzer)):
                    requested_site = flow.request.headers["Host"][0]
                    self.add_to_report("INSECURE_TRANSMISSION",
                                       "Application has leaked sensitive information via insecure transmission. Type: "+key_info+". Value leaked: " + private_info_fuzzer + " in request " + requested_site + flow.request.path)
        AnalyzerDecorator.handle_request(self,flow)
