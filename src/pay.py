from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock

import subprocess
import requests
import json
import re
from functools import partial

from src.backarrow import BackArrow
from src.loading import Loading
from src.homemodal import HomeModal

class Pay(Screen):
    qrcode_url = StringProperty('')
    count_down_num = NumericProperty(60)
    go_home_schedule = ObjectProperty()
    count_down_schedule = ObjectProperty()
    order_state_schedule = ObjectProperty()

    def __init__(self, **kwargs):
        super(Pay, self).__init__(**kwargs)

        self.popup = Popup(title='Warning', content=Label(text=''), size_hint=(None, None), size=(400, 400))
        self.loading = Loading()
        self.homemodal = HomeModal()

    def on_enter(self):
        self.qrcode_url = ''
        self.count_down_num = 60
        self.go_home_schedule = Clock.schedule_once(self._show_gohome_modal, 180)
        Window.bind(on_touch_down=self._listen_screen_touch)

        if self._init_qrcode():
            self.count_down_schedule = Clock.schedule_once(self._count_down, 1)
            self.order_state_schedule = Clock.schedule_interval(self._listen_order_state, 5)

    def on_pre_leave(self):
        Window.unbind(on_touch_down=self._listen_screen_touch)

        if self.go_home_schedule:
            self.go_home_schedule.cancel()
        if self.count_down_schedule:
            self.count_down_schedule.cancel()
        if self.order_state_schedule:
            self.order_state_schedule.cancel()

    def _print(self):
        # self.popup.dismiss()
        self.loading.open()

        app = App.get_running_app()
        path = 'tmp/download.data'

        process = subprocess.Popen('lp -n ' + str(app.num_copies) + ' ' + path, shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()

        if err:
            print('print error, ' + str(err))
            self._show_warning('Printing Error Occurred，Please Contact Service Center')
        else:
            job_id = self._get_job_id(out)
            print('job id is ' + job_id)
            Clock.schedule_once(partial(self._listen_printer_job, job_id))

    def _listen_printer_job(self, time, job_id):
        if job_id:
            queue = subprocess.Popen('lpstat -o', shell=True, stdout=subprocess.PIPE).communicate()[0]
            if str(job_id) in str(queue):
                Clock.schedule_once(partial(self._listen_printer_job, job_id), 1)
                return
        self.loading.dismiss()
        self.manager.current = 'complete'

    def _get_job_id(self, out):
        reg = re.compile('.*is\s(.*)\s\(.*')
        try:
            job_id = reg.match(str(out)).group(1)
            return job_id
        except Exception as e:
            print('get print job id failed, ' + str(e))
            return None

    def _listen_order_state(self, time):
        app = App.get_running_app()
        try:
            print('get order state---->')
            url = 'https://printer-test-api.iremi.com/order/pay/status?id=' + app.order_id
            if 'userId' in app.file_info:
                url += ('&userId=' + app.file_info['userId'])
            req = requests.get(url)
            res = req.json()
            print('order state response----->')
            print(res)
            errcode = res['errcode']
            if res['errcode'] != 0:
                self._show_warning(str(errcode))
                return False
            status = res['data']['status']
            if status == 1:
                self._pay_success()
            elif status == 2:
                self._pay_error()
        except Exception as e:
            print(e)
            self._show_warning('Get Order Status Error')
            return False

    def _pay_success(self):
        self.count_down_schedule.cancel()
        self.order_state_schedule.cancel()
        # self._show_success('Order Success')
        # Clock.schedule_once(self._print, 3)
        self._print()

    def _pay_error(self):
        self.count_down_schedule.cancel()
        self.order_state_schedule.cancel()
        # self._show_success('Order Success')
        # Clock.schedule_once(self._print, 3)
        self._show_warning('Payment Failed')
        Clock.schedule_once(self._go_home, 2)

    def _go_home(self, time):
        self.manager.current = 'home'

    def _init_qrcode(self):
        qrcode_url = self._get_qrcode()
        if not qrcode_url:
            self._show_warning('Something error')
            return False
        # self.qrcode_url = 'http://store-images.s-microsoft.com/image/apps.33967.13510798887182917.246b0a3d-c3cc-46fc-9cea-021069d15c09.392bf5f5-ade4-4b36-aa63-bb15d5c3817a?mode=scale&q=90&h=270&w=270&background=%230078D7'
        self.qrcode_url = qrcode_url.replace('https', 'http', 1)
        return True

    def _count_down(self, time):
        if self.count_down_num == 0 and self._init_qrcode():
            self.count_down_num = 60
            self.count_down_schedule = Clock.schedule_once(self._count_down, 1)
            return
        self.count_down_num -= 1
        self.count_down_schedule = Clock.schedule_once(self._count_down, 1)

    def _get_qrcode(self):
        app = App.get_running_app()
        data = {"id": app.order_id, "type": 0}
        if 'userId' in app.file_info:
            data['userId'] = app.file_info['userId']

        try:
            print('get qrcode---->')
            print(data)
            headers = {'content-type':'application/json'}
            req = requests.post('https://printer-test-api.iremi.com/order/pay/qrcode', data=json.dumps(data), headers=headers)
            res = req.json()
            print('qrcode response----->')
            print(res)
            errcode = res['errcode']
            if res['errcode'] != 0:
                self._show_warning(str(errcode))
                return False
            return res['data']['url']
        except Exception as e:
            print(e)
            self._show_warning('Get Qrcode Error')
            return False

    def _listen_screen_touch(self, instance, event):
        if self.go_home_schedule:
            self.go_home_schedule.cancel()
        self.go_home_schedule = Clock.schedule_once(self._show_gohome_modal, 180)

    def _show_gohome_modal(self, *args, **kwargs):
        self.homemodal.open()

    def _show_warning(self, msg):
        print(msg)
        self.loading.dismiss()
        self.popup.auto_dismiss = True
        self.popup.title = 'Warning'
        self.popup.content.text = msg
        self.popup.open()

    def _show_success(self, msg):
        print(msg)
        self.loading.dismiss()
        self.popup.auto_dismiss = False
        self.popup.title = 'Success'
        self.popup.content.text = msg
        self.popup.open()
