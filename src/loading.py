from kivy.uix.modalview import ModalView
from kivy.uix.image import Image

class Loading(ModalView):
    def __init__(self, **kwargs):
        super(Loading, self).__init__(**kwargs)

        self.size_hint = (None, None)
        self.auto_dismiss = False
        self.add_widget(Image(source='assets/loading.gif', size_hint=(None, None), size=(400, 400)))