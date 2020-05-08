from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.network.urlrequest import UrlRequest
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.logger import Logger

import requests
import sys

from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session, exceptions

from src.custombtn import ConfirmBtn, CancelBtn
from src.backarrow import BackArrow
from src.loading import Loading

keyboard_arr = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['OK', '0', '']
]

class BookingCode(Screen):
    code = StringProperty('')
    clicked = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(BookingCode, self).__init__(**kwargs)

        self.popup = Popup(title='Error', content=Label(text=''), size_hint=(None, None), size=(400, 400))
        self.loading = Loading()

        keyboard = Keyboard()
        self.keyboard = keyboard
        self.add_widget(keyboard)

    def on_pre_enter(self, *args):
        self.code = ''
        self.clicked = False
        App.get_running_app().file_info = None
        App.get_running_app().detail_back_screen = 'bookingcode'

    def submit(self):
        if not self.code:
            self._show_error('Invalid booking number')
            return

        if self.clicked:
            return
        self.clicked = True

        self.loading.open()

        Clock.schedule_once(self._request, .5)

    def _request(self, *args, **kwargs):
        file_info = self._get_file_info()

        if not file_info:
            return

        App.get_running_app().file_info = file_info
        file_url = file_info['fileUrl']

        if App.get_running_app().fetchFile(file_url):
            self.manager.current = 'detail'
            self.loading.dismiss()
        else:
            self._show_error('Network error, please try again later.')

    def _get_file_info(self):
        try:
            res = App.get_running_app().rest_get('file/booknumber?bookNumber=' + self.code)
            if res['errcode'] != 0:
                self._show_error('Invalid booking number')
            else:
                return res['data']
        except Exception as e:
            Logger.exception(e)
            self._show_error('Network error, please try again later.')

    def _show_error(self, msg):
        Logger.info(msg)
        self.loading.dismiss()
        self.popup.content.text = msg
        self.popup.open()
        self.clicked = False

    def _on_type(self, text):
        self.code += text

    def _on_delete(self):
        self.code = self.code[0:-1]

    def _on_ok(self):
        self.submit()

class Keyboard(RelativeLayout):

    def __init__(self, **kwargs):
        super(Keyboard, self).__init__(**kwargs)

        self._layout()

    def _layout(self):
        for idx, row in enumerate(keyboard_arr):
            for idy, item in enumerate(row):
                pos_x = (62 + 31) * idy
                pos_y = (32 + 14) * (3 - idx)
                btn = Key(text=item, pos=(pos_x, pos_y))
                if item == 'OK':
                    btn.background_color = [.85, .89, .97, 1]
                    btn.color = [.49, .62, .89, 1]
                if not item:
                    btn.add_widget(Image(pos=(pos_x + 23, pos_y + 10), size_hint=(None, None), size=(19, 12), source='assets/delete.png', allow_stretch=True))
                self.add_widget(btn)

    def _on_type(self, text):
        if text == 'OK':
            self.parent._on_ok()
        elif not text:
            self.parent._on_delete()
        else:
            self.parent._on_type(text)

class Key(Button):

    def on_press(self):
        self.background_color[3] = .7

    def on_release(self):
        self.background_color[3] = 1
