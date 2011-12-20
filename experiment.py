import kivy
from kivy.logger import Logger

kivy.require('1.0.7') # replace with your current kivy version !

from kivy.app import App

from random import random, randint
from threading import Timer

from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.floatlayout import FloatLayout
#from kivy.uix.gridlayout import GridLayout
#from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.logger import Logger
from kivy.core.audio import Sound, SoundLoader

# default value for color of object and target
grab_low_color = Color(0.86, 0.28, 0.078)
grab_high_color = Color(0.86, 0.28, 0.078)
release_low_color = Color(0.0,0.0, 0.7, 0.5)
release_high_color = Color(0.86, 0.28, 0.078)

screen_width = 1920
screen_height = 1080
record_number = 0
vertical_border = 90 #1080 / 12
horizontal_border = 160 #1920 / 12
min_obj_width = 10
max_obj_width = 190 #actual maximum will be min_obj_width + max_obj_width

class Object(Widget):
    def __init__(self, gesture):
        Widget.__init__(self)
        if (gesture == 'grab'):
            self.img = Image(source='img/ball_2.png', pos_hint=(10,10), color=(0.7,0.5,0.3,0.9), size=(300,300))
        elif (gesture == 'release'):
            self.img = Image(source='img/hole_2.png', pos_hint=(10,10), color=(0.7,0.5,0.3,0.9), size=(300,300))
        else:
            print "error in creating object"
            
        self.add_widget(self.img)
        #self.size=(50,50)
        #self.pos=(250,300)
    
    #give a new random size to this object
    def scale(self):
        d = min_obj_width + round(max_obj_width*random())
        self.img.size=(d, d)
    
    #move this obj to a new random location
    def move(self):
        self.img.pos=(horizontal_border+round((screen_width - 2 * horizontal_border)*random()), vertical_border+round((screen_height - 2 * vertical_border)*random()))
        #self.img.pos_hint=(10,10)

    def set_color(self, color):
        self.img.color=color


class Root(Widget):
    # gesture codes
    grab_gesture = 1
    release_gesture = 2
    hand_gesture_offset = 256
    grab_obj = Object(gesture='grab')
    release_obj = Object(gesture='release')

    def start(self):
        self.size=(600,500)
        self.add_widget(self.grab_obj) 
        self.add_widget(self.release_obj)
        
    def on_touch_down(self, touch):
        if not 'markerid' in touch.profile:
            self.next_trial()
            return
        hand_id = int(touch.fid / self.hand_gesture_offset)
        gesture_id = touch.fid % self.hand_gesture_offset
        if gesture_id == self.grab_gesture:
            self.grab_obj.set_color((0.7,0.5,0.3,0.3))
            self.release_obj.set_color((0.6,0.2,0.4,0.9))
        if gesture_id == self.release_gesture:
            self.next_trial()

    def next_trial(self):
        self.grab_obj.scale()
        self.release_obj.scale()
        self.grab_obj.move()
        self.grab_obj.set_color((0.7,0.5,0.3,0.9))
        self.release_obj.move()
        self.release_obj.set_color((0.6,0.2,0.4,0.8))
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

