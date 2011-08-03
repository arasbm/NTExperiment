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
	def __init__(self, ws_count, width=1920, height=1080):
		# some predefined variables differ from their default value for multitouch case
		self.enable_slide = True
		self.slide_threshold = 200
		self.enable_border_slide = True
		self.prevent_edge = False
		# call parent
		ContainerBase.__init__(self, ws_count=ws_count, width=width, height=height)
	
	def on_touch_down (self, touch):
		# if object touched call it's on_touch_down function and disable panning workspaces
		# by returning True

		print touch.ud

		"""
		"  grab  "
		"""
		if self.my_object != None and self.my_object.collide_point(touch.x-self.x, touch.y-self.y):
			self.my_object.dispatch('on_touch_down', touch)
			# TODO maybe keep touch itself in my_object, instead of it's ud
			self.object_moving = True
			self.my_object.owner_id = touch.ud
			self.play_grab_sound()
			self.object_grabbed_event()
			return True
		# calls same function in it's ancestor
		# keeps x-location of touch, to use for sliding the workspace later
		Scatter.on_touch_down(self, touch)
		"""
		"  sense sliding  "
		"""
		self.initial_x = touch.x

	def on_touch_up (self, touch):
		# calls same function in it's ancestor, and slides the workspace
		Scatter.on_touch_up(self, touch)
		"""
		"  starts sliding  "
		"""
		if self.initial_x != None and (not self.object_moving or touch.ud != self.my_object.owner_id):
			current = self.current_workspace()
			# self.current_trial.ws_switch += 1
			if self.x <= 0 and (-1*self.x) % self.single_width() != 0:
				if self.initial_x > touch.x:
					if abs(self.initial_x - touch.x) > self.slide_threshold:
						current = current + 1
						if current >= len(self.frames):
							current = len(self.frames) - 1
						else:
							self.workspace_slide_event()
				else:
					current = current
					if abs(self.initial_x - touch.x) < self.slide_threshold:
						current = current + 1
					else:
						self.workspace_slide_event()
			self.slide(current)
			self.initial_x = None
		# if touch lefts from a target trigger that target
		"""
		"  release  "
		"""
		if self.object_moving and touch.ud == self.my_object.owner_id:
			if self.sliding:
				self.stop_slide = True
			self.object_moving = False
			self.play_release_sound()
			tx = touch.x
			ty = touch.y
			tx = self.push_out_border (tx, self.single_width())
			ty = self.push_out_border (ty, self.height)
			self.my_object.relocate(tx - self.x, ty - self.y)
			self.object_released_event()
			# if object is released on target, swap them and make a new target
			if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
				"""
				"  collide  "
				"""
				self.object_collide_event()
				self.swap_object_target()
				self.play_collide_sound()
			else:
				self.my_object.move_back()
			self.my_object.owner_id = None

		# TODO no idea about this - to be removed
		if self.my_target != None and self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
			self.my_target.dispatch('on_touch_up', touch)
			return True
		return False

	def on_touch_move (self, touch):
		if self.object_moving and touch.ud == self.my_object.owner_id:
			tx = touch.x
			ty = touch.y
			tx = self.push_out_border (tx, self.single_width())
			ty = self.push_out_border (ty, self.height)
			self.my_object.relocate(tx - self.x, ty - self.y)
			"""
			"  border slide  "
			"""
			if self.enable_border_slide:
				if self.on_right_border(touch) and not self.sliding:
					self.sliding = True
					Timer(self.border_delay,self.slide_right).start()
				if self.on_left_border(touch) and not self.sliding:
					self.sliding = True
					Timer(self.border_delay,self.slide_left).start()
				if not self.on_right_border(touch) and not self.on_left_border(touch) and self.sliding:
					self.stop_slide = True
			"""
			"  highlight target  "
			"""
			if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
				self.my_target.highlight(True)
			else:
				self.my_target.highlight(False)
		if not self.object_moving or touch.ud != self.my_object.owner_id:
			Scatter.on_touch_move(self, touch)

class WorkspaceApp(App):
	def build(self):
		root = Widget()
		# here we add an instance of container to the window, ws_count shows number of workspaces we need
		root.add_widget(Container(ws_count=7))
		return root

def log_time_action(action):
	Logger.info('something: ' + action + ' @' + str(time.time()))

if __name__ in ('__main__', '__android__'):
	log_time_action('start')
	WorkspaceApp().run()
