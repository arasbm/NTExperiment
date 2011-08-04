import time
import sys
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

from touchbase import Workspace, Object, Target, Trial

class ContainerBase(Scatter):
	# workspace may have an object and a target in it
	my_object = None
	my_target = None
	# state of the object in this workspace
	object_moving = False
	# graphical margin of canvas
	margin = 10
	# enable sliding by hand, not to be confused with enable_border_slide
	enable_slide = False

	# list of workspaces will be saved in this variable
	frames = None
	# where user starts sliding the workspace (used for later use in on_touch_up)
	initial_x = None
	# duration of automatic sliding
	anim_duration = 0.5
	# minimum value of panning required for automatic sliding
	slide_threshold = 50

	# enable/disable sliding by going to border, not to be confused with enable_slide
	enable_border_slide = False
	# workspaces are sliding or not (if so, do not consider further slide commands)
	sliding = False
	# if user returns the object from border, so even if Timer is triggered, it shouldn't slide the workspace
	stop_slide = False
	# border size
	border_size = 200
	# threshold time that user should keep the object in border to start border sliding
	border_delay = 0.5

	# gesture codes
	grab_gesture = 1
	release_gesture = 2

	########################
	hand_gesture_offset = 256

	# if application should play sounds
	enable_sound = True

	# saves current trial information
	current_trial = None

	# prevent object from going to edges
	prevent_edge = True

	# max number of trials
	max_trial = 100

	def __init__(self, ws_count, width=900, height=600):
		# container is a scatter that just can be panned in x (horizontal) direction
		Scatter.__init__(self, size=(width*ws_count, height), pos=(0, 0), do_scale=False, do_translation_y=False, do_rotation= False)
		self.do_translation_x = False
		# boxlayout lets us put some workspaces beside eachother
		layout = BoxLayout(orientation='horizontal')
		self.frames = []
		# disable scrolling if we only have one workspace
		scroll = (ws_count > 1)
		# create ws_count
		for i in range(ws_count):
			frame = Workspace(height=height, width=width, scroll=scroll)
			self.frames.append(frame)
			layout.add_widget(frame)
		self.add_widget(layout)
		# for now container will have a random object and target
		self.create_random_object()
		self.my_object.x = self.my_object.x % self.single_width()
		self.my_object.draw()
		self.create_random_target()

		self.current_trial = Trial()
		self.update_trial_dimensions()

	# updates object and target places in trial object
	def update_trial_dimensions(self):
		self.current_trial.object_x = self.my_object.x % self.single_width()
		self.current_trial.object_y = self.my_object.y
		self.current_trial.object_w = self.which_workspace(self.my_object.x)
		self.current_trial.target_x = self.my_target.x % self.single_width()
		self.current_trial.target_y = self.my_target.y
		self.current_trial.target_w = self.which_workspace(self.my_target.x)

	# returns a random value for size
	def random_size(self):
		base = 200
		step = 50
		max_levels = 0
		return base+step*int(max_levels*random())

	# returns a random value with limit, considering margin
	def random_x_dimension(self):
		return int(random()*len(self.frames))*self.single_width() + 4*self.border_size + 4*self.margin + random() * (self.single_width() - 8*self.border_size - 8*self.margin)

	def random_y_dimension(self):
		return 4*self.border_size + random() * (self.height - 8*self.border_size)

	# function to create a random object, which user should drag/move to target
	def create_random_object(self):
		x=self.random_x_dimension()
		y=self.random_y_dimension()
		self.my_object = Object(x=x, y=y, size=self.random_size())
		self.add_widget(self.my_object)
	
	def which_workspace(self, x):
		return int (x / self.single_width())

	# function to create a random target for object
	def create_random_target(self):
		if self.my_target != None:
			self.remove_widget(self.my_target)
		x=self.random_x_dimension()
		y=self.random_y_dimension()
		self.my_target = Target(x=x, y=y, size=self.random_size())
		self.add_widget(self.my_target)
		# adding appropriate borders
		mark_from = self.which_workspace(self.my_object.x)
		mark_to = self.which_workspace(self.my_target.x)
		for f in self.frames:
			f.right_border = f.left_border = False
		for i in range (len(self.frames)):
			if i > mark_to:
				self.frames[i].left_border = True
			elif i < mark_to:
				self.frames[i].right_border = True
		for f in self.frames:
			f.draw()

	def single_width(self):
		return self.width / len(self.frames)

	def current_workspace(self):
		if self.x > 0:
			current = 0
		else:
			current = int(-1 * self.x / self.single_width())
		return current
	
	def slide_right(self):
		self.sliding = False
		if self.stop_slide:
			self.stop_slide = False
			return
		if not self.enable_border_slide:
			return
		current = self.current_workspace()
		if current < len(self.frames) - 1:
			current += 1
			self.workspace_slide_event()
		self.slide(current)
		self.sliding = True
		if self.enable_border_slide:
			Timer(self.border_delay+self.anim_duration,self.slide_right).start()

	def slide_left(self):
		self.sliding = False
		if self.stop_slide:
			self.stop_slide = False
			return
		if not self.enable_border_slide:
			return
		current = self.current_workspace()
		if current > 0:
			current -= 1
			self.workspace_slide_event()
		self.slide(current)
		self.sliding = True
		if self.enable_border_slide:
			Timer(self.border_delay+self.anim_duration,self.slide_left).start()

	def slide (self, ws):
		anim = Animation (x = -1 * ws * self.single_width(), duration=self.anim_duration)
		anim.start(self)

	def swap_object_target(self):
		self.current_trial.log()
		self.current_trial.reset()
		if self.current_trial.trial_number == self.max_trial:
			sys.exit(0)
		self.my_object.x, self.my_object.y = self.my_target.x, self.my_target.y
		self.my_object.width, self.my_object.height = self.my_target.width, self.my_target.height
		self.my_object.draw()
		self.create_random_target()
		self.update_trial_dimensions()

	def on_left_border (self, touch):
		x = (touch.x - self.x) % self.single_width()
		return x < 2*self.border_size

	def on_right_border (self, touch):
		x = (touch.x - self.x) % self.single_width()
		return x > self.single_width() - 2*self.border_size


	def draw (self):
		layout = BoxLayout(orientation='horizontal')
		for frame in self.frames:
			frame.draw()
			layout.add_widget(frame)
		self.add_widget(layout)
		self.my_object.draw()
		self.add_widget(self.my_object)
		self.my_target.draw()
		self.add_widget(self.my_target)

	def push_out_border (self, value, maximum):
		if not self.prevent_edge:
			return value
		border = self.border_size * 1
		if value < border:
			value = border
		if value > maximum - border:
			value = maximum - border
		return value

	def play_grab_sound(self):
		self.play_sound('sound/grab.wav')

	def play_release_sound(self):
		self.play_sound('sound/release.wav')

	def play_collide_sound(self):
		self.play_sound('sound/collide.wav')

	def play_sound(self, filename):
		if self.enable_sound:
			sound = SoundLoader.load(filename=filename)
			if not sound:
				# unable to load this sound?
				pass
			else:
				# sound loaded, let's play!
				sound.play()

	def object_grabbed_event(self):
		print 'object grabbed',
		if self.current_trial.state == 'initial':
			self.current_trial.start_time = time.time()
			self.current_trial.state = 'started'
			print 'and trial started'
		else:
			print ''

	def object_released_event(self):
		print 'object released'
		self.current_trial.release_count += 1

	def object_collide_event(self):
		print 'collide happened', 
		if self.current_trial.state == 'started':
			self.current_trial.end_time = time.time()
			self.current_trial.state = 'ended'
			print 'and trial ended'
		else:
			print 'but in an inapropriate state! state =', self.current_trial.state

	def workspace_slide_event(self):
		print 'sliding happened',
		if self.current_trial.state == 'started':
			self.current_trial.ws_switch += 1
			print 'and counted'
		else:
			print 'but not counted'

	def on_key_down(self, key):
		print key
