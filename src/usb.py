from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.filechooser import FileChooser
from kivy.uix.filechooser import FileChooser, FileChooserIconLayout
from kivy.clock import Clock

import os
from pathlib import Path
from shutil import copyfile

from src.backarrow import BackArrow
from src.custombtn import ConfirmBtn

file_filters = ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx', '*.ppt', '*.pptx']

# print(11111, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
class Usb(Screen):
    schedule = ObjectProperty()

    def on_enter(self):
        self.confirmBtn.disable()
        app = App.get_running_app()
        app.file_info = None
        usb_path = app.udisk_path
        chooser = UDiskChooser(size=(self.width - 100, self.height - 150), usb_path=usb_path)
        self.chooser = chooser
        self.add_widget(self.chooser)

        self._scan_udisk()

    def on_leave(self):
        self.remove_widget(self.chooser)
        if self.schedule: self.schedule.cancel()

    def on_confirm_select(self):
        if self.chooser.file_chooser.selection:
            self._choose_file()

    def _choose_file(self, *args, **kwargs):
        app = App.get_running_app()
        file_path = self.chooser.file_chooser.selection[0]
        copyfile(file_path, 'tmp/download.data')
        file_name = file_path.split('/')[-1]
        app.file_info = {'name': file_name, 'email': ''}
        app.root.current = 'detail'

    def _scan_udisk(self, *args, **kwargs):
        udisk_path = App.get_running_app().udisk_path
        if not Path(udisk_path).exists():
            print('udisk umounted')
            self.manager.current = 'usbguide'
            return
        self.schedule = Clock.schedule_once(self._scan_udisk, 1)

    def _change_btn_status(self, *args, **kwargs):
        if self.chooser.file_chooser.selection:
            self.confirmBtn.enable()
        else:
            self.confirmBtn.disable()

class UDiskChooser(RelativeLayout):
    usb_path = StringProperty('')

    def __init__(self, **kwargs):
        super(UDiskChooser, self).__init__(**kwargs)

        file_chooser = FileChooser(
            rootpath=self.usb_path,
            filters=file_filters,
            on_submit=self.choose_file,
            on_touch_up=self._on_touch_down)
        self.file_chooser = file_chooser
        file_chooser.add_widget(FileChooserIconLayout())

        self.add_widget(file_chooser)

    def choose_file(self, *args, **kwargs):
        self.parent._choose_file()

    def _on_touch_down(self, instance, touch):
        if instance.collide_point(*touch.pos):
            Clock.schedule_once(self._listen_file_selection, .3)

    def _listen_file_selection(self, *args, **kwargs):
        if self.parent:
            self.parent._change_btn_status()
