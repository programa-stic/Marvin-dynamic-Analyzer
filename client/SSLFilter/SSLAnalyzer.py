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

# DummyAnalyzer for testing
class SSLAnalyzer(Analyzer):
    @staticmethod
    def is_for(filter_id):
        # attend Dummy
        return filter_id in [
            "SSL_CUSTOM_TRUSTMANAGER",
            "SSL_CUSTOM_HOSTNAMEVERIFIER",
            "SSL_ALLOWALL_HOSTNAMEVERIFIER",
            "SSL_INSECURE_SOCKET_FACTORY",
            "SSL_WEBVIEW_ERROR"
        ]

    def handle_request(self, flow):
        if flow.request.scheme.endswith("https"):
            self.add_to_report(self.get_filter_id(),
                               'SSL connection to host %s, app not validating certificates properly' % (
                               flow.request.headers["Host"][0] + flow.request.path))
        Analyzer.handle_request(self,flow)

