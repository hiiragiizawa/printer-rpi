from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ListProperty, StringProperty
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.lang import Builder

class CustomBtn(ButtonBehavior, RelativeLayout):

    background_color = ListProperty()
    text = StringProperty()

    def on_press(self):
        self.background_color[3] = .7

    def on_release(self):
        self.background_color[3] = 1


class ConfirmBtn(CustomBtn):
    background_color = ListProperty([.84, .88, .96, 1])
    text_color = ListProperty([.18, .38, .84, 1])

    def disable(self):
        self.background_color = [.93, .93, .93, 1]
        self.text_color = [.75, .75, .76, 1]

    def enable(self):
        self.background_color = [.84, .88, .96, 1]
        self.text_color = [.18, .38, .84, 1]

class CancelBtn(CustomBtn):
    background_color = ListProperty([1, 1, 1, 1])

# wait to reconstruction
class ConfirmBtnS(CustomBtn):
    background_color = ListProperty([.84, .88, .96, 1])

Builder.load_file('src/custombtn.kv')
