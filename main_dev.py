import os
os.environ['KIVY_GL_BACKEND'] = 'gl'

# use local config
from kivy.config import Config
Config.read('settings.dev.ini')
Config.write()

# set background color
from kivy.core.window import Window
Window.clearcolor = (255, 255, 255, 255)

from src.router import PrinterApp

if __name__ == '__main__':
    PrinterApp().run()
