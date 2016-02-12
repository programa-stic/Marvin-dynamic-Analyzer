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


import subprocess
import shlex
import os
import sqlite3
import traceback
from Emulator import Emulator
import settings


class StorageAnalyzer(object):
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def sensitiveValues(self):
        return settings.FUZZER_VALUES

    def extracted_storage_dir(self):
        return self.analyzer.get_package_name() + "_files"

    def internal_storage_dir(self):
        return self.extracted_storage_dir() + "/internal_storage/"

    def modified_sdcard_dir(self):
        return self.extracted_storage_dir() + "/sdcard_modified_files/"

    def extract_storage(self):
        emulator = Emulator.get_emulator()
        directory = self.extracted_storage_dir()
        if not os.path.exists(directory):
            os.makedirs(directory)
        # dump internal memory and sdcard
        emulator.run_adb_command(
            "pull /data/data/" + self.analyzer.get_package_name() + " " + self.internal_storage_dir())
        emulator.run_adb_command("pull /sdcard/" + " " + self.modified_sdcard_dir())

    def is_database(self, fileName):
        cmd = shlex.split('file {0}'.format(fileName))
        result = subprocess.check_output(cmd)
        type = result.split(':')[1]
        return 'SQLite' in type

    def get_filter_id(self):
        return "INSECURE_STORAGE"

    def search_for_plaintext_in_db(self, connection, table, database):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM '{0}';".format(table))
        for row in cursor:
            for keyword, value in self.sensitiveValues().iteritems():
                if value in row:
                    self.analyzer.add_to_report(self.get_filter_id(),
                        "Found plaintext {0} (value {1}) in table {2} of database {3}".format(keyword, value, table,
                                                                                              database))

    def search_for_plaintext(self, file):
        content = open(file).read()
        for keyword, value in self.sensitiveValues().iteritems():
            if value in content:
                self.analyzer.add_to_report(self.get_filter_id(),
                    "Found plaintext {0} (value {1}) in file {2}".format(keyword, value, file))

    def analyze_shared_preferences(self, path):
        self.analyze_files(path)

    def analyze_files(self, path):
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filePath = os.path.join(subdir, file)
                self.search_for_plaintext(filePath)

    def analyze_storage(self):
        self.extract_storage()
        self.analyze_database(self.internal_storage_dir() + 'databases/')
        self.analyze_shared_preferences(self.internal_storage_dir() + 'shared_prefs/')
        self.analyze_files(self.internal_storage_dir() + 'files/')

    def analyze_database(self, path):
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filePath = os.path.join(subdir, file)
                try:
                    if self.is_database(filePath):
                        con = sqlite3.connect(filePath)
                        cursor = con.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        for table in cursor:
                            self.search_for_plaintext_in_db(con, table[0], filePath)
                except:
                    print "Error " + filePath
                    print traceback.format_exc()
