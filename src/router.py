from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock

from pathlib import Path
import configparser
import subprocess

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
            config.read('config.ini')
            self.api_host = config['API']['HOST']
            self.api_version = config['API']['VERSION']
        except Exception:
            self.api_host = 'https://printer-test-api.iremi.com'

    def build(self):
        return Router(transition=NoTransition())

    def on_start(self):
        print('start')
        self.homemodal = HomeModal()
        self.root_schedule = Clock.schedule_once(self._show_gohome_modal, 60)
        Window.bind(on_touch_down=self._listen_screen_touch)

    def _get_mac_address(self):
        mac_address = ''
        if Path('/sys/class/net/eth0/address').exists():
            with open('/sys/class/net/eth0/address', 'r') as file:
                mac_address = file.read()[0:17]
        elif Path('/sys/class/net/eth1/address').exists():
            with open('/sys/class/net/eth1/address', 'r') as file:
                mac_address = file.read()[0:17]
        else:
            mac_address = 'read mac error'
        return mac_address

    def _get_ip(self):
        ip_address = ''
        ip_address = subprocess.getoutput("hostname -I");

        return ip_address
        # queue = subprocess.Popen('hostname -I', shell=True, stdout=subprocess.PIPE).communicate()[0]

    def _show_gohome_modal(self, *args, **kwargs):
        if self.root.current in ['home', 'pay']:
            return
        self.homemodal.open()

    def _listen_screen_touch(self, instance, event):
        self.root_schedule.cancel()
        self.root_schedule = Clock.schedule_once(self._show_gohome_modal, 60)

    def on_stop(self):
        print('stop')
