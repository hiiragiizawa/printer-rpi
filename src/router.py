from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.logger import Logger

from pathlib import Path
import configparser
import subprocess

import requests
import sys
import json
import uuid


from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter

from src.home import Home
from src.bookingcode import BookingCode
from src.complete import Complete
from src.detail import Detail
from src.pay import Pay
from src.payselector import PaySelector
from src.error import Error
from src.usb import Usb
from src.usbguide import UsbGuide
from src.qrguide import QrGuide
from src.homemodal import HomeModal

class Router(ScreenManager):
    def __init__(self, **kwargs):
        super(Router, self).__init__(**kwargs)

        # must load .kv file, unless put these to build method of PrinterApp
        Builder.load_file('src/home.kv')
        self.add_widget(Home(name='home'))

        Builder.load_file('src/bookingcode.kv')
        self.add_widget(BookingCode(name='bookingcode'))

        Builder.load_file('src/complete.kv')
        self.add_widget(Complete(name='complete'))

        Builder.load_file('src/detail.kv')
        self.add_widget(Detail(name='detail'))

        Builder.load_file('src/pay.kv')
        self.add_widget(Pay(name='pay'))

        Builder.load_file('src/error.kv')
        self.add_widget(Error(name='error'))

        Builder.load_file('src/usb.kv')
        self.add_widget(Usb(name='usb'))

        Builder.load_file('src/usbguide.kv')
        self.add_widget(UsbGuide(name='usbguide'))

        Builder.load_file('src/qrguide.kv')
        self.add_widget(QrGuide(name='qrguide'))

        Builder.load_file('src/payselector.kv')
        self.add_widget(PaySelector(name='payselector'))

class PrinterApp(App):

    def __init__(self, **kwargs):
        super(PrinterApp, self).__init__(**kwargs)

        self.detail_back_screen = ''
        self.udisk_path = ''
        self.mac_address = self._get_mac_address()
        self.ip_address = self._get_ip()
        config = configparser.ConfigParser()
        try:
            subprocess.run("git -C /var/app/printer-rpi reset --hard");
            subprocess.run("git -C /var/app/printer-rpi pull");
            config.read('config.ini')
            self.api_host = config['API']['HOST']
            self.api_version = config['API']['VERSION']
        except Exception:
            self.api_host = 'https://remi.print4u.com.my'
            self.api_version = '0.0'

    def build(self):
        return Router(transition=NoTransition())

    def on_start(self):
        print('start')
        self.homemodal = HomeModal()
        self.root_schedule = Clock.schedule_once(self._show_gohome_modal, 60)
        Window.bind(on_touch_down=self._listen_screen_touch)

    def _get_mac_address(self):
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        return mac_address

    def _get_ip(self):
        ip_address = subprocess.getoutput("hostname -I");
        git -C /var/app/printer-rpi pull
        return ip_address

    def _show_gohome_modal(self, *args, **kwargs):
        if self.root.current in ['home', 'pay']:
            return
        self.homemodal.open()

    def _listen_screen_touch(self, instance, event):
        self.root_schedule.cancel()
        self.root_schedule = Clock.schedule_once(self._show_gohome_modal, 60)

    def on_stop(self):
        print('stop')

    def rest_get(self, api):
        Logger.info('REST GET: ' + self.api_host + '/' + api)
        ses = requests.Session()
        retries = Retry(
            total = 3,
            read = 3,
            connect = 5,
            backoff_factor = 0.3,
        )
        ses.mount("https://", HTTPAdapter(max_retries=retries))
        ses = requests.get(self.api_host + '/' + api)
        Logger.info('RESPONSE: ' + ses.text);
        return ses.json();

    def rest_post(self, api, data):
        Logger.info('REST POST: ' + self.api_host + '/' + api)
        Logger.info('DATA: ' + str(data))
        ses = requests.Session()
        retries = Retry(
            total = 3,
            connect = 5,
            backoff_factor = 0.3,
        )
        ses.mount("https://", HTTPAdapter(max_retries=retries))
        ses = requests.post(self.api_host + '/' + api, data=json.dumps(data), headers={'content-type':'application/json'})
        Logger.info('RESPONSE: ' + ses.text);
        return ses.json();
