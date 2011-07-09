import kivy
kivy.require('1.0.6')

from random import random, randint

from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView

from kivy.animation import Animation

from kivy.properties import StringProperty

from kivy.graphics import Line, Ellipse, Color

class MyWidget(Widget):
	def __init__(self):
		Widget.__init__(self)		
		with self.canvas:
			Color (1,1,1)
			Line(points=(100,100,2000,2000))
		clrbtn = Button(text='Reset')
		def reset_canvas(obj):
			children = self.children[:]
			self.canvas.clear()
			with self.canvas:
				Color (1,1,1)
				Line(points=(100,100,2000,2000))
			for child in children:
				self.add_widget(child)
		clrbtn.bind(on_release=reset_canvas)
		self.add_widget(clrbtn)

	def on_touch_down(self, touch):
		with self.canvas:
			Color (1,0,0)
			Ellipse(pos=(touch.x-5, touch.y-5), size=(10, 10))
			Color (*(random(),random(),random()))
			touch.ud['whatever'] = Line(points=(touch.x, touch.y, touch.y, touch.x))
		for child in self.children[:]:
			child.dispatch('on_touch_down', touch)

	def on_touch_move(self, touch):
		if 'whatever' in touch.ud:
			touch.ud['whatever'].points += [touch.x, touch.y, touch.y, touch.x]

	def on_touch_up(self, touch):
		if 'whatever' in touch.ud:
			with self.canvas:
				Color (0,0,1)
				Ellipse(pos=(touch.x-5, touch.y-5), size=(10, 10))

class Window(Scatter):
	def __init__(self):
		Scatter.__init__(self, pos=(200,200), size=(300,300))
		layout = BoxLayout(pos=(50, 50), size=(200,200))
		btn1 = Button(text='Hello')
		btn2 = Button(text='World')
		layout.add_widget(btn1)
		layout.add_widget(btn2)
		self.add_widget(Image(source='img/background.jpg', size=(300,300)))
		self.add_widget(layout)

class Workspace(ScrollView):
	initial_y = None

	def __init__(self):
		ScrollView.__init__(self, size_hint=(None, None), size=(1000, 1000), pos=(0, 0))
		layout = GridLayout(cols=1, spacing=0, size_hint_y=None)
		for i in range(30):
			btn = Button(text=str(i), size_hint_y=None, height=200)
			layout.add_widget(btn)
		self.add_widget(layout)
	
	def on_touch_down(self, touch):
		ScrollView.on_touch_down (self, touch)
		self.initial_y = self.scroll_y

	def on_touch_up(self, touch):
		ScrollView.on_touch_up (self, touch)
		if self.initial_y == None:
			return
		scroll_y = self.scroll_y
		level_y = int(scroll_y*10)
		level_y = level_y / 10.
		#print scroll_y, level_y, 
		if scroll_y <= self.initial_y:
			if level_y < 0:
				level_y = 0
		else:
			level_y = level_y + 0.1
			if level_y > 1:
				level_y = 1
		#print level_y
		adjust = Animation(scroll_y = level_y, duration=0.3)
		adjust.start(self)
		self.initial_y = None
		return True

class TouchtracerApp(App):
	def build(self):
		root = Widget()

		# trying workspace idea
		workspace = Workspace()
		root.add_widget(workspace)

		return root

if __name__ in ('__main__', '__android__'):
	TouchtracerApp().run()
