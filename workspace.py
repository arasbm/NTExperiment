import kivy
kivy.require('1.0.6')

from kivy.app import App

from random import random, randint

from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image

from kivy.graphics import Color, Ellipse, Rectangle

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"			Class Structure				"
"  * Container is main element of GUI, contains workspaces	"
"  * Container can have some Workspace in it			"
"  * Workspace can have one Object and/or Target		"
"								"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# default value for color of object and target
object_color = Color(1,0,0)
target_color = Color(0,0,1)

# stands for an object that can be dragged or moved to target
class Object(Widget):
	def __init__(self, x, y, size):
		Widget.__init__(self, pos=(x,y), size=(size, size))	
		self.canvas.add(object_color)
		self.canvas.add(Ellipse(pos=(x,y), size=(size, size)))

	def on_touch_down(self, touch):
		print 'object touched'

# stands for a target on a workspace
class Target(Widget):
	def __init__(self, x, y, size):
		Widget.__init__(self, pos=(x,y), size=(size, size))	
		self.canvas.add(target_color)
		self.canvas.add(Ellipse(pos=(x,y), size=(size, size)))

	def on_touch_up(self, touch):
		print 'target touched'

# stands for a workspace, within a container
class Workspace(Scatter):
	# workspace may have an object and a target in it
	my_object = None
	my_target = None
	scroll = False
	# if workspace is colored inside, there's an uncolored margin around it.
	margin = 10
	# color of background
	background = Color(0.8,0.8,0.8)

	# returns a random value for size
	def random_size(self):
		return 10+30*random()

	# returns a random value with limit, considering margin
	def random_value(self,limit):
		return 2*self.margin + random() * (limit - 4*self.margin)

	# function to create a random object, which user should drag/move to target
	def create_random_object(self):
		x=self.random_value(self.width)
		y=self.random_value(self.height)
		self.my_object = Object(x=x, y=y, size=self.random_size())
		self.add_widget(self.my_object)

	# function to create a random target for object
	def create_random_target(self):
		x=self.random_value(self.width)
		y=self.random_value(self.height)
		self.my_target = Target(x=x, y=y, size=self.random_size())
		self.add_widget(self.my_target)

	def __init__(self, width, height, scroll = False):
		Scatter.__init__(self, size=(width, height), size_hint_x=None)
		self.width, self.height, self.scroll = width, height, scroll
		# drawing a frame inside workspace
		self.canvas.add(self.background)
		self.canvas.add(Rectangle(pos=(self.margin, self.margin), size=(width-2*self.margin, height-2*self.margin)))
		# for now all workspaces will have object and target in them
		# TODO remove these codes and call functions from container (or another class controlling the experiment)
		self.create_random_object()
		self.create_random_target()

	def on_touch_down (self, touch):
		# if object touched call it's on_touch_down function and disable panning workspaces
		# by returning True
		if self.my_object != None and self.my_object.collide_point(touch.x-self.x, touch.y-self.y):
			self.my_object.dispatch('on_touch_down', touch)
			return True
		# if panning is explicitly disabled (mostly happens when we have only one workspace)
		# return True anyway, so container won't be panned
		if not self.scroll:
			return True

	def on_touch_up (self, touch):
		# if touch lefts from a target trigger that target
		if self.my_target != None and self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
			self.my_target.dispatch('on_touch_up', touch)

# stands for a set of workspaces
class Container(Scatter):
	frames = None

	def __init__(self, ws_count, width=900, height=600):
		# container is a scatter that just can be panned in x (horizontal) direction
		Scatter.__init__(self, size=(width*ws_count, height), pos=(0, 0), do_scale=False, do_translation_y=False, do_rotation= False)
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
	
	def on_touch_down (self, touch):
		# for now just calls same function in it's ancestor
		# TODO add slipping when half-panned
		Scatter.on_touch_down(self, touch)

class WorkspaceApp(App):
	def build(self):
		root = Widget()
		# here we add an instance of container to the window, ws_count shows number of workspaces we need
		root.add_widget(Container(ws_count=2))
		return root

if __name__ in ('__main__', '__android__'):
	WorkspaceApp().run()
