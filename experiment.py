import sys
import kivy
from kivy.logger import Logger

kivy.require('1.0.7') # replace with your current kivy version !

from kivy.app import App

from random import random, randint
from datetime import datetime
#from threading import Timer

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
grab_low_color = (1.0, 0.65, 0.0, 0.3)
grab_high_color = (1.0, 0.65, 0.0, 0.99)
release_low_color = (1.0,0.2, 0.0, 0.3)
release_high_color = (1.0, 0.2, 0.0, 0.99)

screen_width = 1920
screen_height = 1080
vertical_border = 90 #1080 / 12
horizontal_border = 160 #1920 / 12
min_obj_width = 20
max_obj_width = 480 #actual maximum will be min_obj_width + max_obj_width
max_number_trials = 100 * 2 #each trial consist of a grab and a release record

class Object(Widget):
    def __init__(self, gesture):
        Widget.__init__(self)
        self.gesture = gesture
        if (gesture == 'grab'):
            self.img = Image(source='img/ball_2.png') #, pos_hint=(0,0), color=(0.7,0.5,0.3,0.9), size=(0,0))
        elif (gesture == 'release'):
            self.img = Image(source='img/hole_2.png' ) #, pos_hint=(0,0), color=(0.7,0.5,0.3,0.9), size=(0,0))
        else:
            print "error in creating object"
            
        self.add_widget(self.img)
        #self.label = Label(text=gesture)
        #self.add_widget(self.label)
        #self.size=(50,50)
        #self.pos=(250,300)
    
    #give a new random size to this object
    def scale(self):
        d = min_obj_width + round(max_obj_width*random())
        self.img.size=(d, d)
        #self.size=(d, d)
    
    #move this obj to a new random location. must be scaled first!
    def move(self):
        x_pos = horizontal_border - (self.img.width / 2) + round((screen_width - (2 * horizontal_border))*random())
        y_pos = vertical_border - (self.img.height / 2) + round((screen_height - (2 * vertical_border))*random())
        self.img.pos=(x_pos, y_pos)
        #self.label.text = self.gesture + ' [' + str(self.img.center_x) + ',' + str(self.img.center_y) + ']'
        #self.label.center = self.img.center
        #self.img.pos=(100,0)

    def set_color(self, color):
        self.img.color=color


class Root(Widget):
    # gesture codes
    grab_gesture = 1
    release_gesture = 2
    hand_gesture_offset = 256
    grab_obj = Object(gesture='grab')
    release_obj = Object(gesture='release')
    grab_sound = SoundLoader.load(filename='sound/grab.wav')
    release_sound = SoundLoader.load(filename='sound/release.wav')
    record_number = 0
    log_name = datetime.now().strftime("%A_%d_%B_%Y_%H_%M_%S.log")
    log_file = open(log_name, 'w')
    trial_start_time = trial_finish_time = datetime.now()

    def start(self):
        #self.size=(600,500)
        self.write_headers()
        self.add_widget(self.grab_obj) 
        self.add_widget(self.release_obj)
        
    def on_touch_down(self, touch):
        if not 'markerid' in touch.profile:
            self.next_trial()
            return
        hand_id = int(touch.fid / self.hand_gesture_offset)
        gesture_id = touch.fid % self.hand_gesture_offset
        if gesture_id == self.grab_gesture:
            self.grab_action()
        if gesture_id == self.release_gesture:
            self.release_action()
            self.next_trial()

    #called right after grab event happens which is the start of a new trial
    def grab_action(self):
        self.log(action_type="grab")
        self.record_number += 1
        self.grab_obj.set_color(grab_low_color)
        self.release_obj.set_color(release_high_color)
        self.trial_start_time = datetime.now()
        if self.grab_sound:
            self.grab_sound.play()
            
    #called right after release event happens
    def release_action(self):
        self.log(action_type="release")
        self.record_number += 1
        self.grab_obj.set_color(grab_high_color)
        self.release_obj.set_color(release_low_color)
        self.trial_finish_time = datetime.now()
        if self.release_sound:
            self.release_sound.play()
            
    #add a line to the log
    def log(self, action_type):
        if action_type == "release":
            trial_duration = self.trial_start_time - self.trial_finish_time #this is the actual trial duration
        else:
            trial_duration = self.trial_finish_time - self.trial_start_time  #time passed since last trial

        self.log_file.write( str(self.record_number) + ", " + str(datetime.now()) \
        #.strftime("%d/%m/%y %H:%M:%S") \
        + "," + str(trial_duration) \
        + "," + str(self.grab_obj.img.width) + "," + str(self.grab_obj.img.height) \
        + "," + str(self.grab_obj.img.center_x) + "," + str(self.grab_obj.img.center_y) \
        + "," + str(self.release_obj.img.width) + "," + str(self.release_obj.img.height) \
        + "," + str(self.release_obj.img.center_x) + "," + str(self.release_obj.img.center_y) \
        + "," + action_type + "\n" )
        
    def write_headers(self):
        self.log_file.write( "record_number, datetime, trial_duration, grab_obj.width, grab_obj.height, \
grab_obj.center_x, grab_obj.center_y, release_obj.width, release_obj.height, \
release_obj.center_x, release_obj.img.center_y, action_type\n" )
        
    #reset and position objects for next trial
    def next_trial(self):
        self.grab_obj.scale()
        self.release_obj.scale()
        self.grab_obj.move()
        self.release_obj.move()
        self.grab_obj.set_color(grab_high_color)
        self.release_obj.set_color(release_low_color)
        while self.grab_obj.img.collide_widget(self.release_obj.img):
            self.grab_obj.move()
            self.release_obj.move()
        if self.record_number > max_number_trials:
            print "Thank You!"
            self.log_file.close()
            sys.exit()
        
class TestApp(App):
    def build(self):
        root = Root()
        root.start()
        return root

if __name__ in ('__android__', '__main__'):
    Logger.info("Starting: This is a custom log message")
    TestApp().run()

