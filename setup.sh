#!/bin/bash
apt-get update
apt-get install libreoffice-writer -y
apt-get install libreoffice-calc -y
apt-get install libreoffice-impress -y
apt-get install python3-kivy -y
apt-get install python3-pip -y
apt-get install python3-sdl2 -y
apt-get install python3-opengl -y

python3 -m pip install --upgrade --user pip setuptools
python3 -m pip install --upgrade --user Cython==0.29.10 pillow
python3 -m pip install pdf2image
python3 -m pip install PyPDF3
python3 -m pip install requests
python3 -m pip install kivy_deps.sdl2
