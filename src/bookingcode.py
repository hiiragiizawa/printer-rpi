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

import requests
import sys

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
            self._show_error('Invalid Code')
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

        print(file_info)

        App.get_running_app().file_info = file_info
        file_url = file_info['fileUrl']

        if self._download_file(file_url):
            self.manager.current = 'detail'

    def _get_file_info(self):
        try:
            print('get file info, code is ' + str(self.code))
            req = requests.get('https://printer-test-api.iremi.com/file/booknumber?bookNumber=' + self.code)
            res = req.json()
            print(res)

            if res['errcode'] != 0:
                self._show_error(str(res['errcode']))
            else:
                return res['data']
        except Exception as e:
            print(e)
            self._show_error('Connected Failed')

    def _download_file(self, file_url):
        try:
            with open('tmp/download.data', 'wb') as f:
                # 为了测试，把全部下载链接换成了一张阿里云上面的图片
                # file_url = 'https://remi-images.oss-cn-beijing.aliyuncs.com/cms/10_1476848902861.jpg'
                response = requests.get(file_url, timeout=15)
                total_length = response.headers.get('content-length')

                f.write(response.content)

                # if total_length is None:
                #     f.write(response.content)
                # else:
                #     dl = 0
                #     total_length = int(total_length)
                #     for data in response.iter_content(chunk_size=4096):
                #         dl += len(data)
                #         f.write(data)
                #         done = int(50 * dl / total_length)
                #         sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
                #         sys.stdout.flush()

            self.loading.dismiss()
            return True
        except Exception as e:
            print(e)
            self._show_error('Download Error')

    def _show_error(self, msg):
        print(msg)
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