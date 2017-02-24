#!/usr/bin/bash

# Get mitmproxy files
wget https://github.com/mitmproxy/mitmproxy/archive/v0.11.3.tar.gz
wget https://github.com/mitmproxy/netlib/archive/v0.11.2.tar.gz

# Install requirements
sudo apt-get update
sudo apt-get -y install python-pip
sudo apt-get -y install python-cffi
sudo apt-get -y install libffi-dev
sudo apt-get -y install python-dev
sudo apt-get -y install libssl-dev
sudo apt-get -y install libxml2-dev
sudo apt-get -y install libxslt-dev
sudo apt-get -y install android-tools-adb
sudo pip install --upgrade six
sudo pip install netifaces
sudo pip install --upgrade setuptools

tar xvzf v0.11.2.tar.gz
cd netlib-0.11.2
sudo python setup.py install
cd ..

tar xvzf v0.11.3.tar.gz
cd mitmproxy-0.11.3
sudo python setup.py install


