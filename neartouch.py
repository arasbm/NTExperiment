import time
import kivy
kivy.require('1.0.6')

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

from touchbase import Workspace, Object, Target
from appbase import ContainerBase

# stands for a set of workspaces
class Container(ContainerBase):
	def __init__(self, ws_count, width=900, height=600):
		# call parent
		ContainerBase.__init__(self, ws_count=ws_count, width=width, height=height)
	
	def on_touch_down (self, touch):
		if not 'markerid' in touch.profile:
			return
		hand_id = int(touch.fid / self.hand_gesture_offset)
		gesture_id = touch.fid % self.hand_gesture_offset
		if not self.object_moving and gesture_id == self.grab_gesture:
			self.canvas.clear()
			self.draw()
			self.canvas.add(Ellipse(pos=(touch.x-self.x, touch.y-self.y), size=(30,30)))
			if self.my_object.collide_point(touch.x-self.x, touch.y-self.y):
				print 'object grabbed'
				self.play_grab_sound()
				self.my_object.dispatch('on_touch_down', touch)
				self.object_moving = True
				self.my_object.owner_id = hand_id
				return True
		if self.object_moving and hand_id != self.my_object.owner_id:
			self.initial_x = touch.x
			print 'started sliding'
		# calls same function in it's ancestor
		# keeps x-location of touch, to use for sliding the workspace later
		Scatter.on_touch_down(self, touch)

	def on_touch_up (self, touch):
		# calls same function in it's ancestor, and slides the workspace
		Scatter.on_touch_up(self, touch)
		if not 'markerid' in touch.profile:
			return
		hand_id = int(touch.fid / self.hand_gesture_offset)
		gesture_id = touch.fid % self.hand_gesture_offset
		self.canvas.clear()
		self.draw()
		if self.initial_x != None and self.object_moving and hand_id != self.my_object.owner_id:
			print 'about to slide'
			current = self.current_workspace()
			if self.initial_x > touch.x:
				if abs(self.initial_x - touch.x) > self.slide_threshold:
					current = current + 1
				if current >= len(self.frames):
					current = len(self.frames) - 1
			else:
				if abs(self.initial_x - touch.x) > self.slide_threshold:
					current = current - 1
				if current < 0:
					current = 0
			self.slide(current)
			self.initial_x = None
		return False

	def on_touch_move (self, touch):
		# will not work with simple touch anymore
		if not 'markerid' in touch.profile:
			return
		hand_id = int(touch.fid / self.hand_gesture_offset)
		gesture_id = touch.fid % self.hand_gesture_offset
		if self.object_moving and hand_id == self.my_object.owner_id:
			self.my_object.relocate(touch.x - self.x, touch.y - self.y)
			if self.enable_border_slide:
				if self.on_right_border(touch) and not self.sliding:
					self.sliding = True
					Timer(self.border_delay,self.slide_right).start()
				if self.on_left_border(touch) and not self.sliding:
					self.sliding = True
					Timer(self.border_delay,self.slide_left).start()
				if not self.on_right_border(touch) and not self.on_left_border(touch) and self.sliding:
					self.stop_slide = True
			if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
				self.my_target.highlight(True)
			else:
				self.my_target.highlight(False)
			if gesture_id == self.release_gesture:
				self.object_moving = False
				if play_sound:
					self.play_release_sound()
				if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
					self.swap_object_target()
					self.play_collide_sound()
		if not self.object_moving or touch.ud != self.my_object.owner_id:
			Scatter.on_touch_move(self, touch)
			self.canvas.clear()
			self.draw()
			self.canvas.add(Color(0,0,0))
			self.canvas.add(Ellipse(pos=(touch.x-self.x, touch.y-self.y), size=(30,30)))

class WorkspaceApp(App):
	def build(self):
		root = Widget()
		# here we add an instance of container to the window, ws_count shows number of workspaces we need
		root.add_widget(Container(ws_count=3))
		return root

def log_time_action(action):
	Logger.info('something: ' + action + ' @' + str(time.time()))

if __name__ in ('__main__', '__android__'):
	log_time_action('start')
	WorkspaceApp().run()
