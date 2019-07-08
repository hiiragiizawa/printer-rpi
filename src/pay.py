from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.logger import Logger

import subprocess
import requests
import json
import re
from functools import partial

from src.backarrow import BackArrow
from src.loading import Loading
from src.homemodal import HomeModal

PAY_CHANNEL_NAMES = ['Sarawak Pay', 'Boost', 'Online Payment']
PAY_CHANNEL_LOGOS = ['assets/sarawak-pay-logo.png', 'assets/boost-logo.png', 'assets/online-banking-logo.png']

class Pay(Screen):
    qrcode_url = StringProperty('')
    count_down_num = NumericProperty(60)
    go_home_schedule = ObjectProperty()
    count_down_schedule = ObjectProperty()
    order_state_schedule = ObjectProperty()
    pay_channel_name = ''
    pay_channel_logo = ''
    qrcode = False

    def __init__(self, **kwargs):
        super(Pay, self).__init__(**kwargs)

        self.popup = Popup(title='Warning', content=Label(text=''), size_hint=(None, None), size=(400, 400))
        self.loading = Loading()
        self.homemodal = HomeModal()

    def on_enter(self):
        # self.qrcode_url = ''
        self.qrcode_url = 'assets/loading.gif'
        self.count_down_num = 60
        self.go_home_schedule = Clock.schedule_once(self._show_gohome_modal, 180)
        Window.bind(on_touch_down=self._listen_screen_touch)
        pay_channel = App.get_running_app().pay_channel
        self.pay_channel_name = PAY_CHANNEL_NAMES[pay_channel]
        self.pay_channel_logo = PAY_CHANNEL_LOGOS[pay_channel]
        self.pay_channel_label.text = PAY_CHANNEL_NAMES[pay_channel]
        self.pay_channel_image.source = PAY_CHANNEL_LOGOS[pay_channel]

        Clock.schedule_once(self._delay_init, .5)

    def _delay_init(self, time):
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
            Logger.info('print error, ' + str(err))
            self._show_warning('Printing Error Occurred，Please Contact Service Center')
        else:
            job_id = self._get_job_id(out)
            Logger.info('job id is ' + job_id)
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
            Logger.exception('get print job id failed, ' + str(e))
            return None

    def _listen_order_state(self, time):
        app = App.get_running_app()
        try:
            Logger.info('get order state---->')
            url = App.get_running_app().api_host + '/order/pay/status?id=' + app.order_id
            if 'userId' in app.file_info:
                url += ('&userId=' + app.file_info['userId'])
            req = requests.get(url)
            res = req.json()
            Logger.info('order state response----->')
            Logger.info(res)
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
            Logger.exception(e)

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
        Clock.schedule_once(self._get_qrcode, 1)

    def _count_down(self, time):
        if self.count_down_num == 0 and self._init_qrcode():
            self.count_down_num = 60
            self.count_down_schedule = Clock.schedule_once(self._count_down, 1)
            return
        self.count_down_num -= 1
        self.count_down_schedule = Clock.schedule_once(self._count_down, 1)

    def _get_qrcode(self, time):
        app = App.get_running_app()
        data = {"id": app.order_id, "type": app.pay_channel}
        if 'userId' in app.file_info:
            data['userId'] = app.file_info['userId']

        try:
            Logger.info(data)
            headers = {'content-type':'application/json'}
            req = requests.post(App.get_running_app().api_host + '/order/pay/qrcode', data=json.dumps(data), headers=headers)
            res = req.json()
            Logger.info(res)
            errcode = res['errcode']
            if res['errcode'] != 0:
                self._show_warning(str(errcode))
                return False
            self.qrcode_url = res['data']['url']
            self.qrcode_url = self.qrcode_url.replace('https', 'http', 1)
            return True
        except Exception as e:
            # Logger.exception(e)
            Logger.info('Network timeout, retrying in 3s')
            Clock.schedule_once(self._get_qrcode, 3);
            return False

    def _listen_screen_touch(self, instance, event):
        if self.go_home_schedule:
            self.go_home_schedule.cancel()
        self.go_home_schedule = Clock.schedule_once(self._show_gohome_modal, 180)

    def _show_gohome_modal(self, *args, **kwargs):
        self.homemodal.open()

    def _show_warning(self, msg):
        Logger.info(msg)
        self.loading.dismiss()
        self.popup.auto_dismiss = True
        self.popup.title = 'Warning'
        self.popup.content.text = msg
        self.popup.open()

    def _show_success(self, msg):
        Logger.info(msg)
        self.loading.dismiss()
        self.popup.auto_dismiss = False
        self.popup.title = 'Success'
        self.popup.content.text = msg
        self.popup.open()
