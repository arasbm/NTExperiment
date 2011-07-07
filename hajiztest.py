import kivy
kivy.require('1.0.6')

from random import random, randint

from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.image import Image

from kivy.properties import StringProperty

from kivy.graphics import Line, Ellipse, Color

class MyWidget(Widget):
	def on_touch_down(self, touch):
		with self.canvas:
			Color (1,0,0)
			Ellipse(pos=(touch.x-5, touch.y-5), size=(10, 10))
			Color (*(random(),random(),random()))
			touch.ud['harchi'] = Line(points=(touch.x, touch.y, touch.y, touch.x))

	def on_touch_move(self, touch):
		if 'harchi' in touch.ud:
			touch.ud['harchi'].points += [touch.x, touch.y, touch.y, touch.x]

	def on_touch_up(self, touch):
		with self.canvas:
			Color (0,0,1)
			Ellipse(pos=(touch.x-5, touch.y-5), size=(10, 10))

class ScatteredButton(Scatter):
	def construct(self):
		item = Button(text='Scale me')
		def alarm(obj):
			print 'do no push me, scale me!!'
		item.bind(on_release=alarm)
		#self.add_widget(item)
		self.add_widget(Image(source='dome.jpg'))
	"""
	def on_touch_down(self, touch):
		super(ScatteredButton, self).on_touch_down(touch)
		print 'touched'
		for child in self.children[:]:
			child.dispatch('on_touch_down', touch)

	def on_touch_up(self, touch):
		super(ScatteredButton, self).on_touch_up(touch)
		for child in self.children[:]:
			child.dispatch('on_touch_up', touch)
	"""

class TouchtracerApp(App):
	def build(self):
		root = Widget()

		# trying custom widget
		painter = MyWidget()
		with painter.canvas:
			Color (1,1,1)
			Line(points=(100,100,2000,2000))
		root.add_widget(painter)

		# trying button
		clrbtn = Button(text='Reset')
		root.add_widget(clrbtn)
		def reset_canvas(obj):
			painter.canvas.clear()
			with painter.canvas:
				Color (1,1,1)
				Line(points=(100,100,2000,2000))
		clrbtn.bind(on_release=reset_canvas)

		# trying scatter 
		picture = Scatter(do_rotation=False, do_scale=True, do_translation_y=False, rotation=0)
		picture.add_widget(Image(source='dome.jpg'))
		root.add_widget(picture)

		# trying nested objects
		container = ScatteredButton(pos=(200,300))
		container.construct()
		root.add_widget(container)

		return root

if __name__ in ('__main__', '__android__'):
	TouchtracerApp().run()
