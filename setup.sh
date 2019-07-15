#!/bin/bash
apt-get update
apt-get install libreoffice-writer
apt-get install libreoffice-calc
apt-get install libreoffice-impress
apt-get install python3-kivy

python3 -m pip install --upgrade setuptools
python3 -m pip install pdf2image
python3 -m pip install PyPDF3
python3 -m pip install requests
