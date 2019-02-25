### used in Raspberry Pi3 B+

### dependence
* python3.7
* kivy1.10.1
* pdf2image
* requests
* PyPDF3

### hardware
* Pi3 b+
* RASPBIAN STRETCH WITH DESKTOP AND RECOMMENDED SOFTWARE
* 4.14
* release date 2018-11-13

#### prepare env
##### 换源（国内必须换） 换源前也可备份下原来的文件

```
    sudo sed -i 's#://raspbian.raspberrypi.org#s://mirrors.tuna.tsinghua.edu.cn/raspbian#g' /etc/apt/sources.list
    sudo sed -i 's#://archive.raspberrypi.org/debian#s://mirrors.tuna.tsinghua.edu.cn/raspberrypi#g' /etc/apt/sources.list.d/raspi.list
```
##### 安装python3.7
```
    sudo apt-get update
    sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

    wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz

    tar xf Python-3.7.0.tar.xz

    cd Python-3.7.0

    ./configure --prefix=/usr/local/opt/python-3.7.0

    make -j 4

    sudo make altinstall

    sudo ln -s /usr/local/opt/python-3.7.0/bin/pydoc3.7 /usr/bin/pydoc3.7
    sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7 /usr/bin/python3.7
    sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7m /usr/bin/python3.7m
    sudo ln -s /usr/local/opt/python-3.7.0/bin/pyvenv-3.7 /usr/bin/pyvenv-3.7
    sudo ln -s /usr/local/opt/python-3.7.0/bin/pip3.7 /usr/bin/pip3.7

    sudo pip3.7 install --upgrade pip
```
##### 安装树莓派环境
```
    sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev pkg-config libgl1-mesa-dev libgles2-mesa-dev python3-setuptools libgstreamer1.0-dev git-core gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-{omx,alsa} python3-dev libmtdev-dev xclip xsel

    sudo pip3.7 install Cython

    sudo pip3.7 install git+https://github.com/kivy/kivy.git@stable-1.10
```
##### 安装第三方依赖包
```
    sudo apt-get update
    sudo apt-get install doppler-utils  // pdf2image依赖
    sudo apt-get install libjpeg-dev zlib1g-dev  // pillow依赖
    sudo pip3.7 install pdf2image
    sudo pip3.7 install requests
```
##### 安装python依赖包
```
    sudo apt-get update
    sudo apt-get install doppler-utils
    sudo apt-get install libjpeg-dev zlib1g-dev
    sudo pip3.7 install pdf2image
    sudo pip3.7 install requests
    sudo pip3.7 install PyPDF3
```

### 运行程序
```
    cd app_path
    python3.7 main.py
```


Deploy


scp -r * pi@192.168.1.8:/home/pi/printer-rpi-RPi
