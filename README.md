### used in Raspberry Pi3 B+

### hardware
* Raspberry Pi 3B+
* RASPBIAN STRETCH WITH DESKTOP AND RECOMMENDED SOFTWARE
* 4.14
* release date 2018-11-13


### preparing for RPI 3B+
```
$ apt-get update
$ apt-get install libreoffice-writer libreoffice-calc libreoffice-impress -y
$ apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
   pkg-config libgl1-mesa-dev libgles2-mesa-dev \
   python-setuptools libgstreamer1.0-dev git-core \
   gstreamer1.0-plugins-{bad,base,good,ugly} \
   gstreamer1.0-{omx,alsa} python-dev libmtdev-dev \
   xclip xsel libjpeg-dev zlib1g-dev doppler-utils -y


$ python3 -m pip install cython==0.28.2 pillow setuptools
$ python3 -m pip install pdf2image PyPDF3 requests
$ python3 -m pip install https://github.com/kivy/kivy/archive/1.11.1.zip

$ mkdir /var/app
$ cd /var/app/
$ git clone https://github.com/hiiragiizawa/printer-rpi.git
```

### setting up cups

```
$ apt-get install cups -y
$ usermod -a -G lpadmin pi

lp -n 1 README.md

```

localhost:631

Administration
1. Set Default Options
2. Set As Server Default

### Configuring App Startup
```
$ nano /etc/rc.local
```
cd /var/app/printer-rpi
/usr/bin/python3 main.py



### Start x11 Service
```
$ startx
```



```
git -C /var/app/printer-rpi pull
```
