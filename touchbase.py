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

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"			Class Structure				"
"  * Container is main element of GUI, contains workspaces	"
"  * Container can have some Workspace in it			"
"  * Container can have one Object and/or Target		"
"								"
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# default value for color of object and target
object_color = Color(0.86, 0.28, 0.078)
target_color = Color(0,0,0.7, 0.5)
target_highlight_color = Color(0,0,1)

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
		print 'wrong'

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
	background = Color(0.8,0.8,0.8, 1)
	direction_color = Color (0.5,0.5,0)
	# border size
	border_size = 100

	right_border = False
	left_border = False

	w, h = None, None

	def __init__(self, width, height, scroll = False):
		Scatter.__init__(self, size=(width, height), size_hint_x=None)
		self.scroll = scroll
		# TODO get rid of w and h variables (problem is that workspace loses his height value
		self.w, self.h = width, height
		self.draw()
		
	def draw(self):
		# drawing a frame inside workspace
		self.canvas.clear()
		self.canvas.add(self.background)
		self.canvas.add(Rectangle(pos=(self.margin, self.margin), size=(self.w-2*self.margin, self.h-2*self.margin)))
		self.canvas.add(self.direction_color)
		if self.right_border:
			self.canvas.add(Rectangle(pos=(self.w-self.border_size, self.margin), size=(self.border_size, self.h-2*self.margin)))
		if self.left_border:
			self.canvas.add(Rectangle(pos=(0, self.margin), size=(self.border_size, self.h-2*self.margin)))

	def on_touch_down (self, touch):
		# if panning is explicitly disabled (mostly happens when we have only one workspace)
		# return True anyway, so container won't be panned
		if not self.scroll:
			return True
		return False

	def on_touch_up (self, touch):
		pass
