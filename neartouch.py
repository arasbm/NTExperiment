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
	border_size = 100
	# threshold time that user should keep the object in border to start border sliding
	border_delay = 0.7

	# gesture codes
	grab_gesture = 1
	release_gesture = 2

	########################
	hand_gesture_offset = 256

	# if application should play sounds
	play_sound = False

	# returns a random value for size
	def random_size(self):
		base = 150
		step = 40
		max_levels = 3
		return base+step*int(max_levels*random())

	# returns a random value with limit, considering margin
	def random_x_dimension(self):
		return int(random()*len(self.frames))*self.single_width() + 3*self.border_size + 3*self.margin + random() * (self.single_width() - 6*self.border_size - 6*self.margin)

	def random_y_dimension(self):
		return 3*self.border_size + random() * (self.height - 6*self.border_size)

	# function to create a random object, which user should drag/move to target
	def create_random_object(self):
		x=self.random_x_dimension() % self.single_width()
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

	def __init__(self, ws_count, width=900, height=600):
		# container is a scatter that just can be panned in x (horizontal) direction
		Scatter.__init__(self, size=(width*ws_count, height), pos=(0, 0), do_scale=False, do_translation_y=False, do_rotation= False)
		self.do_translation_x = self.enable_slide
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
		self.create_random_target()

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
				if play_sound:
					sound = SoundLoader.load(filename='sound/grab.wav')
					if not sound:
						# unable to load this sound?
						pass
					else:
						# sound loaded, let's play!
						sound.play()
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
		self.slide(current)
		self.sliding = True
		Timer(self.border_delay,self.slide_right).start()

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
		self.slide(current)
		self.sliding = True
		Timer(self.border_delay,self.slide_left).start()

	def slide (self, ws):
		anim = Animation (x = -1 * ws * self.single_width(), duration=self.anim_duration)
		anim.start(self)

	def swap_object_target(self):
		self.my_object.x, self.my_object.y = self.my_target.x, self.my_target.y
		self.my_object.width, self.my_object.height = self.my_target.width, self.my_target.height
		self.my_object.draw()
		self.create_random_target()

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

	def on_left_border (self, touch):
		return (touch.x - self.x) % self.single_width() < self.border_size

	def on_right_border (self, touch):
		return (touch.x - self.x) % self.single_width() > self.single_width() - self.border_size

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
					sound = SoundLoader.load(filename='sound/release.wav')
					if not sound:
						# unable to load this sound?
						pass
					else:
						# sound loaded, let's play!
						sound.play()
				if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
					self.swap_object_target()
					if play_sound:
						sound = SoundLoader.load(filename='sound/collide.wav')
						if not sound:
							# unable to load this sound?
							pass
						else:
							# sound loaded, let's play!
							sound.play()
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
