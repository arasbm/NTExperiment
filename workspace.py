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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"			Class Structure				"
"  * Container is main element of GUI, contains workspaces	"
"  * Container can have some Workspace in it			"
"  * Container can have one Object and/or Target		"
"								"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# default value for color of object and target
object_color = Color(1,0,0)
target_color = Color(0,0,1)
target_highlight_color = Color(0,1,0)

# stands for an object that can be dragged or moved to target
class Object(Widget):
	initial_x, initial_y = None, None
	owner_id = None

	def __init__(self, x, y, size):
		Widget.__init__(self, pos=(x,y), size=(size, size))
		self.initial_x, self.initial_y = x, y
		self.draw()

	def relocate(self, x, y):
		size = self.width
		self.x = x - size / 2
		self.y = y - size / 2
		self.draw()

	def draw(self):
		self.canvas.clear()
		self.canvas.add(object_color)
		self.canvas.add(Ellipse(pos=(self.x,self.y), size=(self.width, self.height)))

	def on_touch_down(self, touch):
		pass

	def move_back(self):
		pass

# stands for a target on a workspace
class Target(Widget):
	highlighted = False

	def __init__(self, x, y, size):
		Widget.__init__(self, pos=(x,y), size=(size, size))	
		self.draw()

	def draw(self):
		self.canvas.clear()
		if not self.highlighted:
			self.canvas.add(target_color)
		else:
			self.canvas.add(target_highlight_color)
		self.canvas.add(Ellipse(pos=(self.x,self.y), size=(self.width, self.height)))

	def on_touch_up(self, touch):
		pass

	def highlight(self, on):
		self.highlighted = on
		self.draw()

# stands for a workspace, within a container
class Workspace(Scatter):
	scroll = False
	# if workspace is colored inside, there's an uncolored margin around it.
	margin = 10
	# color of background
	background = Color(0.8,0.8,0.8)

	def __init__(self, width, height, scroll = False):
		Scatter.__init__(self, size=(width, height), size_hint_x=None)
		self.width, self.height, self.scroll = width, height, scroll
		# drawing a frame inside workspace
		self.canvas.add(self.background)
		self.canvas.add(Rectangle(pos=(self.margin, self.margin), size=(width-2*self.margin, height-2*self.margin)))
		
	def on_touch_down (self, touch):
		# if panning is explicitly disabled (mostly happens when we have only one workspace)
		# return True anyway, so container won't be panned
		if not self.scroll:
			return True
		return False

	def on_touch_up (self, touch):
		pass

# stands for a set of workspaces
class Container(Scatter):
	# workspace may have an object and a target in it
	my_object = None
	my_target = None
	# state of the object in this workspace
	object_moving = False
	# graphical margin of canvas
	margin = 10
	# enable sliding by hand, not to be confused with enable_border_slide
	enable_slide = True

	# list of workspaces will be saved in this variable
	frames = None
	# where user starts sliding the workspace (used for later use in on_touch_up)
	initial_x = None
	# duration of automatic sliding
	anim_duration = 0.2
	# minimum value of panning required for automatic sliding
	slide_threshold = 200

	# enable/disable sliding by going to border, not to be confused with enable_slide
	enable_border_slide = True
	# workspaces are sliding or not (if so, do not consider further slide commands)
	sliding = False
	# if user returns the object from border, so even if Timer is triggered, it shouldn't slide the workspace
	stop_slide = False
	# border size
	border_size = 100
	# threshold time that user should keep the object in border to start border sliding
	border_delay = 1

	# returns a random value for size
	def random_size(self):
		return 10+30*random()

	# returns a random value with limit, considering margin
	def random_dimension(self,limit):
		return 4*self.margin + random() * (limit - 8*self.margin)

	# function to create a random object, which user should drag/move to target
	def create_random_object(self):
		x=self.random_dimension(self.width)
		y=self.random_dimension(self.height)
		self.my_object = Object(x=x, y=y, size=self.random_size())
		self.add_widget(self.my_object)

	# function to create a random target for object
	def create_random_target(self):
		if self.my_target != None:
			self.remove_widget(self.my_target)
		x=self.random_dimension(self.width)
		y=self.random_dimension(self.height)
		self.my_target = Target(x=x, y=y, size=self.random_size())
		self.add_widget(self.my_target)

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
	
	def on_touch_down (self, touch):
		# if object touched call it's on_touch_down function and disable panning workspaces
		# by returning True
		if self.my_object != None and self.my_object.collide_point(touch.x-self.x, touch.y-self.y):
			self.my_object.dispatch('on_touch_down', touch)
			# TODO maybe keep touch itself in my_object, instead of it's ud
			self.object_moving = True
			self.my_object.owner_id = touch.ud
			return True
		# calls same function in it's ancestor
		# keeps x-location of touch, to use for sliding the workspace later
		Scatter.on_touch_down(self, touch)
		self.initial_x = touch.x

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
		if self.initial_x != None:
			current = self.current_workspace()
			if self.x <= 0 and (-1*self.x) % self.single_width() != 0:
				if self.initial_x > touch.x:
					if abs(self.initial_x - touch.x) > self.slide_threshold:
						current = current + 1
					if current >= len(self.frames):
						current = len(self.frames) - 1
				else:
					current = current
					if abs(self.initial_x - touch.x) < self.slide_threshold:
						current = current + 1
			self.slide(current)
			self.initial_x = None
		# if touch lefts from a target trigger that target
		if self.object_moving and touch.ud == self.my_object.owner_id:
			if self.sliding:
				self.stop_slide = True
			self.object_moving = False
			self.my_object.relocate(touch.x - self.x, touch.y - self.y)
			# if object is released on target, swap them and make a new target
			if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
				self.swap_object_target()
			else:
				self.my_object.move_back()
		if self.my_target != None and self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
			self.my_target.dispatch('on_touch_up', touch)
			return True
		return False

	def on_left_border (self, touch):
		return (touch.x - self.x) % self.single_width() < self.border_size

	def on_right_border (self, touch):
		return (touch.x - self.x) % self.single_width() > self.single_width() - self.border_size

	def on_touch_move (self, touch):
		if self.object_moving and touch.ud == self.my_object.owner_id:
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
		if not self.object_moving or touch.ud != self.my_object.owner_id:
			Scatter.on_touch_move(self, touch)

class WorkspaceApp(App):
	def build(self):
		root = Widget()
		# here we add an instance of container to the window, ws_count shows number of workspaces we need
		root.add_widget(Container(ws_count=3))
		return root

if __name__ in ('__main__', '__android__'):
	WorkspaceApp().run()
