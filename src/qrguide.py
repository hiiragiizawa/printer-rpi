from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger

import requests
import sys

from src.backarrow import BackArrow
from src.loading import Loading

class QrGuide(Screen):
    code = StringProperty()
    isRequesting = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(QrGuide, self).__init__(**kwargs)

        self.popup = Popup(title='Error', content=Label(text=''), size_hint=(None, None), size=(400, 400))
        self.loading = Loading()

    def on_pre_enter(self):
        self.code = ''
        self.isRequesting = False
        App.get_running_app().file_info = None
        App.get_running_app().detail_back_screen = 'qrguide'

        self._keyboard_init()

    def on_leave(self):
        self._keyboard_closed()

    def _keyboard_init(self):
        self._keyboard = Window.request_keyboard(self._callback, self, 'number')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _callback(self):
        Logger.info('keyboard want to close')

    def _keyboard_closed(self):
        Logger.info('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.isRequesting:
            Logger.info('requesting, please wait')
            return False

        print(keycode, text, modifiers)

        if keycode[0] >= 48 and keycode[0] <= 57:
            self.code += text
        #
        if keycode[0] == 13:
            self.submit()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def submit(self):
        self.isRequesting = True

        if not self.code:
            self._show_error('Invalid Code')
            return

        self.loading.open()
        Clock.schedule_once(self._request, .5)

    def _request(self, *args, **kwargs):
        file_info = self._get_file_info()

        if not file_info:
            return

        Logger.info(file_info)

        App.get_running_app().file_info = file_info
        file_url = file_info['fileUrl']

        if self._download_file(file_url):
            self.manager.current = 'detail'

    def _get_file_info(self):
        try:
            res = App.get_running_app().rest_get('file/booknumber?bookNumber=' + self.code)
            if res['errcode'] != 0:
                self._show_error('Invalid Code')
            else:

                return res['data']
        except Exception as e:
            Logger.info("Network timeout, retry in 3s")
            self._show_error('Connected Failed')

    def _download_file(self, file_url):
        try:
            with open('tmp/download.data', 'wb') as f:

                response = requests.get(file_url, timeout=15)
                total_length = response.headers.get('content-length')

                f.write(response.content)

            self.loading.dismiss()
            return True
        except Exception as e:
            Logger.exception(e)
            self._show_error('Download Error')

    def _show_error(self, msg):
        Logger.info(msg)
        self.loading.dismiss()
        self.popup.content.text = msg
        self.popup.open()
        self.isRequesting = False
        self.code = ''
