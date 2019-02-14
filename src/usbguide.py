from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import ObjectProperty

import subprocess

from src.backarrow import BackArrow

def sh(command, print_msg=True):
    p = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    if print_msg:
        print(result)
    return result

class UsbGuide(Screen):
    schedule = ObjectProperty()

    def __init__(self, **kwargs):
        super(UsbGuide, self).__init__(**kwargs)

    def _scan_udisk(self, *args):
        letters = sh('ls -a /media/pi')
        letter_list = letters.split('\n')
        letter_list = list(filter(None, letter_list))
        last_letter = letter_list[-1]
        if last_letter not in ['.', '..']:
            App.get_running_app().udisk_path = '/media/pi/' + last_letter
            self.manager.current = 'usb'
            return

        self.schedule = Clock.schedule_once(self._scan_udisk, 1)

    def on_enter(self):
        App.get_running_app().detail_back_screen = 'usbguide'

        self._scan_udisk()

    def on_leave(self):
        if self.schedule:
            self.schedule.cancel()
