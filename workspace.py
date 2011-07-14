import kivy
kivy.require('1.0.6')

from kivy.app import App

from random import random, randint

from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from kivy.graphics import Color, Rectangle

class Workspace(ScrollView):
	def __init__(self, ws_count, width=900, height=600):
		ScrollView.__init__(self, size_hint=(None, None), size=(width, height), pos=(0, 0))
		layout = GridLayout(rows=1, spacing=0, size_hint_x=None)
		for i in range(ws_count):
			btn = Button(text=str(i), height=height, width=width)
			layout.add_widget(btn)
		self.add_widget(layout)

class WorkspaceApp(App):
	def build(self):
		root = Widget()
		root.add_widget(Workspace(ws_count=3))
		return root

if __name__ in ('__main__', '__android__'):
	WorkspaceApp().run()
