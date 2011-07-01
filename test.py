import kivy
from kivy.logger import Logger

kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image

class TestApp(App):
    def build(self):
        scatter = Scatter()
        object_red = Image(source='img/ball_red.png')
        scatter.add_widget(object_red)
        return scatter

if __name__ in ('__android__', '__main__'):
    Logger.info("Starting: This is a custom log message")
    TestApp().run()

