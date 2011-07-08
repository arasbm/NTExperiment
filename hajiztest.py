import kivy
kivy.require('1.0.6')

from random import random, randint

from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.image import Image

from kivy.animation import Animation

from kivy.properties import StringProperty

from kivy.graphics import Line, Ellipse, Color

class MyWidget(Widget):
	def on_touch_down(self, touch):
		with self.canvas:
			Color (1,0,0)
			Ellipse(pos=(touch.x-5, touch.y-5), size=(10, 10))
			Color (*(random(),random(),random()))
			touch.ud['whatever'] = Line(points=(touch.x, touch.y, touch.y, touch.x))

	def on_touch_move(self, touch):
		if 'whatever' in touch.ud:
			touch.ud['whatever'].points += [touch.x, touch.y, touch.y, touch.x]

	def on_touch_up(self, touch):
		if 'whatever' in touch.ud:
			with self.canvas:
				Color (0,0,1)
				Ellipse(pos=(touch.x-5, touch.y-5), size=(10, 10))

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
		picture.add_widget(Image(source='img/dome.jpg'))
		root.add_widget(picture)

		# trying nested objects
		window = Scatter(pos=(200,200), size=(300,300))
		layout = BoxLayout(pos=(50, 50), size=(200,200))
		btn1 = Button(text='Hello')
		btn2 = Button(text='World')
		layout.add_widget(btn1)
		layout.add_widget(btn2)
		window.add_widget(Image(source='img/background.jpg', size=(300,300)))
		window.add_widget(layout)
		root.add_widget(window)

		return root

if __name__ in ('__main__', '__android__'):
	TouchtracerApp().run()
