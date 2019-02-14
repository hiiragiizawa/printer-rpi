from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock

import os
from pdf2image import convert_from_path
from pathlib import Path
from shutil import move
import tempfile
import PyPDF3
import requests
import json
import subprocess
from functools import partial

from src.backarrow import BackArrow
from src.custombtn import ConfirmBtn, ConfirmBtnS
from src.loading import Loading

# default_info = {'id': '287976392019283968', 'userId': '280772321789218816', 'email': '39627596@qq.com', 'name': 'IMG_2313.HEIC', 'size': 1551340.0, 'type': 'image/jpeg', 'fileUrl': 'https://s3.amazonaws.com/printer7212b9b1d7bf4475aef6e7d93e2fd4b4/public/undefined_IMG_2313.HEIC', 'uploadTime': 1542786923000, 'updateTime': 1542786923000, 'status': 0, 'bookNumber': '10000087'}

class PreviewImage(Image):
    source = StringProperty()

class Detail(Screen):
    file_name = StringProperty()
    email = StringProperty()
    detail_back_screen = StringProperty()
    page_count = NumericProperty(0)
    page_max = NumericProperty(0)
    unit_price = NumericProperty(0.5)
    preview_area = ObjectProperty()

    def __init__(self, **kwargs):
        super(Detail, self).__init__(**kwargs)

        self.popup = Popup(title='Warning', content=Label(text=''), size_hint=(None, None), size=(400, 400))
        self.loading = Loading()

    def on_enter(self):
        self._clear_preview()

        app = App.get_running_app()
        file_info = app.file_info
        self.counter.num = 1

        if 'name' in file_info:
            self.file_name = file_info['name']
        if 'email' in file_info:
            self.email = file_info['email']

        self.detail_back_screen = app.detail_back_screen

        self._get_printer_state()
        self._init_file(file_info)

    def _get_printer_state(self):
        mac_address = App.get_running_app().mac_address
        try:
            req = requests.get('https://printer-test-api.iremi.com/cms/printer/getbymac?address=' + mac_address)
            res = req.json()
            print(res)
            if res['errcode'] != 0:
                self._show_warning('Printer disconnected')
                Clock.schedule_once(self._go_home, 3)
                return
            data = res['data']
            self.printer_id = data['id']
            self.paper_max = min(data['paperSurplus'], data['inkSurplus'])
            self.unit_price = data['unitPrice']
        except Exception as e:
            print(e)
            self._go_home()

    def _go_home(self, *args, **kwargs):
        self.manager.current = 'home'

    def _clear_preview(self):
        if self.preview_area:
            self.preview_area.clear_widgets()
        if Path('tmp/firstPage.jpg').exists():
            os.remove('tmp/firstPage.jpg')

    def preview(self):
        app = App.get_running_app()

        file_fmt = app.file_info['name'].split('.')[-1].lower()
        # not_preview = True
        # not_preview = not_preview and (file_fmt not in ['jpg', 'png', 'pdf', 'jpeg'])
        # if not_preview and 'type' in app.file_info:
        #     not_preview = not_preview and ('image' not in app.file_info['type'])
        # if not_preview:
        #     self._show_warning('Only .jpg, .png and .pdf files can be previewd')
        #     return

        path = 'tmp/download.data'

        # if the file is not images, transfer the first page to jpg file and save to tmp folder to preview
        if not file_fmt in ['jpg', 'png', 'jpeg']:
            with tempfile.TemporaryDirectory() as path1:
                images_from_path = convert_from_path(path, dpi=50, output_folder=path1, last_page=1, fmt='jpg')
                first_page = images_from_path[0]
                first_page.save('tmp/firstPage.jpg')
                image = PreviewImage(source='tmp/firstPage.jpg')
                image.reload()
                self.preview_area.add_widget(image)
        else:
            image = PreviewImage(source=path)
            image.reload()
            self.preview_area.add_widget(image)

    def on_leave(self):
        self.preview_area.clear_widgets()

    def _show_warning(self, msg):
        print(msg)
        self.loading.dismiss()
        self.popup.content.text = msg
        self.popup.open()

    def _init_file(self, file_info):
        file_fmt = file_info['name'].split('.')[-1].lower()
        if file_fmt in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']:
            self.loading.open()
            Clock.schedule_once(partial(self._convert_file, file_info), .5)
        else:
            self._set_page_count(file_info)

    def _go_back(self, later):
        self.manager.current = self.detail_back_screen

    def _convert_file(self, file_info, later):
        cwd = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'tmp'))
        subprocess.Popen('soffice --headless --convert-to pdf download.data', shell=True, cwd=cwd).wait()

        if not Path('tmp/download.pdf').exists():
            self._show_warning('Convert file error')
            Clock.schedule_once(self._go_back, 3)
            return

        move('tmp/download.pdf', 'tmp/download.data')
        self.loading.dismiss()
        self._set_page_count(file_info)

    def _set_page_count(self, file_info):
        file_type = file_info['name'].split('.')[-1].lower()
        file_path = 'tmp/download.data'

        if file_type in ['jpg', 'png', 'jpeg']:
            self.page_count = 1
            print('image file page count:' + str(self.page_count))
        else:
            self._set_pdf_page_count(file_path)

    def _set_pdf_page_count(self, path):
        pdfFileObj = open(path, 'rb')
        pdfReader = PyPDF3.PdfFileReader(pdfFileObj)
        self.page_count = pdfReader.numPages
        print('pdf file page count:' + str(self.page_count))

    def confirm(self):
        total_page_count = self.page_count * self.counter.num
        if total_page_count > self.paper_max:
            self._out_of_limit()
            return
        self.loading.open()
        Clock.schedule_once(self._request, .5)

    def _request(self, *args, **kwargs):
        total_page_count = self.page_count * self.counter.num
        total_price = self.unit_price * total_page_count
        order_id = self._create_order(total_page_count, total_price)
        print('order_id: ' + str(order_id))
        app = App.get_running_app()
        app.total_price = total_price
        print('total price is ' + str(total_price))
        if order_id:
            app.order_id = order_id
            app.num_copies = self.counter.num
            self.loading.dismiss()
            self.manager.current = 'pay'

    def _create_order(self, total_page_count, total_price):
        data = {"id": self.printer_id, "paper": total_page_count, "money": total_price}
        file_info = App.get_running_app().file_info
        keys = ['bookNumber', 'userId']
        for key in keys:
            if key in file_info:
                data[key] = file_info[key]

        try:
            print('order data---->')
            print(data)
            headers = {'content-type':'application/json'}
            req = requests.post('https://printer-test-api.iremi.com/order/submit', data=json.dumps(data), headers=headers)
            res = req.json()
            errcode = res['errcode']
            if res['errcode'] == 31010:
                self._out_of_limit()
                return False
            elif res['errcode'] != 0:
                self._show_warning(str(errcode))
                return False
            return res['data']['orderId']
        except Exception as e:
            print(e)
            self._show_warning('Submit Error')
            return False

    def _out_of_limit(self):
        self.loading.dismiss()
        self.manager.current = 'error'

class Counter(RelativeLayout):
    num = NumericProperty(1)

    def reduce(self):
        if self.num >= 2:
            self.num -= 1

    def add(self):
        self.num += 1