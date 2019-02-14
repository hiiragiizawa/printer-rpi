from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.properties import StringProperty

class BackArrow(Button):
    image_source = StringProperty('assets/backArrow.png')

Builder.load_file('src/backarrow.kv')