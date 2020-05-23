## Hardware Requirement
* Raspberry Pi 3B+
* RASPBIAN STRETCH WITH DESKTOP AND RECOMMENDED SOFTWARE
* 4.14
* release date 2018-11-13

## System Environment
#### Preparing Environment for Raspbian System to install Print4U software
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
```

#### Setup installation directory and settings
```
$ mkdir /var/app
$ cd /var/app/
$ git clone https://github.com/hiiragiizawa/printer-rpi.git
$ cd /var/app/printer-rpi
$ cp settings.sample.ini settings.ini
```

#### Setup CUPS for printing
```
$ apt-get install cups -y
$ usermod -a -G lpadmin pi

lp -n 1 README.md

```
#### Steps for configuring CUPS from website
URL: localhost:631

Administration
1. Set Default Options
2. Set As Server Default


## Preparing Print4U System
#### Configuring App Startup

Command for opening system startup file
```
$ nano /etc/rc.local
```

Add the following command to rc.local file to startup Print4U software on system startup
```
/usr/bin/python3 /var/app/printer-rpi/main.py
```

#### Manual Update for Print4U Software
```
$ git -C /var/app/printer-rpi pull
```


## Other Useful Command
#### Start x11 Service (Raspbian GUI)
```
$ startx
```

#### Update System Certificate
```
$ sudo apt-get install apt-transport-https ca-certificates -y
$ sudo update-ca-certificates
```
