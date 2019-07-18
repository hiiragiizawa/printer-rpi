#!/bin/bash
apt-get update
apt-get install libreoffice-writer libreoffice-calc libreoffice-impress -y
apt-get install python3-pip -y
apt-get install cups -y
apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
   pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   python-setuptools libgstreamer1.0-dev git-core \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} python-dev libmtdev-dev \
   xclip xsel libjpeg-dev -y

python3 -m pip install cython==0.28.2 pillow setuptools
python3 -m pip install pdf2image PyPDF3 requests
python3 -m pip install https://github.com/kivy/kivy/archive/master.zip
