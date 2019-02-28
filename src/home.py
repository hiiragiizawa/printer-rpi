from kivy.uix.screenmanager import Screen

class Home(Screen):
    version_no = 1

    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)
        self.demo()

    def demo(self):
        print("hello")
