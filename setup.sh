#!/bin/bash
apt-get update
apt-get install libreoffice-core
apt-get install python3-kivy

python3 -m pip install --upgrade setuptools
python3 -m pip install pdf2image
python3 -m pip install PyPDF3
python3 -m pip install requests
