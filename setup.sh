#!/bin/bash
apt-get update
apt-get install libreoffice-writer -y
apt-get install libreoffice-calc -y
apt-get install libreoffice-impress -y
apt-get install python3-kivy -y
apt-get install python3-pip -y

python3 -m pip install --upgrade setuptools
python3 -m pip install pdf2image
python3 -m pip install PyPDF3
python3 -m pip install requests
