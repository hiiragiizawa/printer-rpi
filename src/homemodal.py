from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.app import App

class HomeModal(ModalView):
    count_down_num = 10

    def __init__(self, **kwargs):
        super(HomeModal, self).__init__(**kwargs)

        self.background_color = [1, 1, 1, .7]
        self.size_hint = (None, None)

    def on_open(self, *args, **kwargs):
        self.count_down.text = str(self.count_down_num) + 's'
        self.cdschedule = Clock.schedule_interval(self._count_down, 1)

    def on_dismiss(self, *args, **kwargs):
        self.cdschedule.cancel()
        self.count_down_num = 10

    def _count_down(self, *args, **kwargs):
        if self.count_down_num == 0:
            # dissmiss and go home
            self.dismiss()
            App.get_running_app().root.current = 'home'
            return
        self.count_down_num -= 1
        self.count_down.text = str(self.count_down_num) + 's'

Builder.load_file('src/homemodal.kv')
