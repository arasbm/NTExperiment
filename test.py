import kivy
from kivy.logger import Logger

kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App

from random import random, randint
from threading import Timer

from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.logger import Logger
from kivy.core.audio import Sound, SoundLoader

# default value for color of object and target
object_color = Color(0.86, 0.28, 0.078)
target_color = Color(0,0,0.7, 0.5)

class Object(Widget):
    def __init__(self):
        Widget.__init__(self)	
        self.img = Image(source='img/particle.png', pos_hint=(10,10), color=(0.7,0.5,0.3,0.9), size=(300,300))
        self.add_widget(self.img)
        #self.size=(50,50)
        #self.pos=(250,300)
    
    def move(self):
        self.img.pos=(round(600*random()), round(500*random()))
        #self.img.pos_hint=(10,10)

class Root(Widget):
    grab_obj = Object()
    release_obj = Object()
		
    def start(self):
        self.size=(600,500)
        self.add_widget(self.grab_obj) 
        self.add_widget(self.release_obj)
        
    def on_touch_down(self, touch):
        self.next_trial()
        
    def next_trial(self):
        self.grab_obj.move()
        self.release_obj.move()
        while self.grab_obj.img.collide_widget(self.release_obj.img):
            self.grab_obj.move()
            self.release_obj.move()
        print "Trial"
        
class TestApp(App):
    def build(self):    
        root = Root()
        root.start()  
        return root
        
    

if __name__ in ('__android__', '__main__'):
    Logger.info("Starting: This is a custom log message")
    TestApp().run()

