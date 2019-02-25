from kivy.app import App
from kivy.uix.screenmanager import Screen

from src.backarrow import BackArrow

class PaySelector(Screen):

    def on_select(self, channel):
        App.get_running_app().pay_channel = channel
        self.manager.current = 'pay'
