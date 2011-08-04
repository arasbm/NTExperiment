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
from kivy.core.window import Window

from touchbase import Workspace, Object, Target
from appbase import ContainerBase

# stands for a set of workspaces
class Container(ContainerBase):
	def __init__(self, ws_count, width=1920, height=1080):
		# call parent
		ContainerBase.__init__(self, ws_count=ws_count, width=width, height=height)
		print 'start at', time.strftime('%H:%M:%S %y/%m/%d', time.localtime())
		print 'mode : bimanual neartouch'
	
	def on_touch_down (self, touch):
		if not 'markerid' in touch.profile:
			return
		hand_id = int(touch.fid / self.hand_gesture_offset)
		gesture_id = touch.fid % self.hand_gesture_offset
		if not self.object_moving and gesture_id == self.grab_gesture:
			self.canvas.clear()
			self.draw()
			self.canvas.add(Ellipse(pos=(touch.x-self.x, touch.y-self.y), size=(30,30)))
			"""
			"  grab  "
			"""
			if self.my_object.collide_point(touch.x-self.x, touch.y-self.y):
				self.play_grab_sound()
				# does not seem necessary
				# self.my_object.dispatch('on_touch_down', touch)
				self.object_moving = True
				self.my_object.owner_id = hand_id
				self.object_grabbed_event()
				return True

		# keeps x-location of touch, to use for sliding the workspace later
		"""
		"  sense sliding  "
		"""
		if self.object_moving and hand_id != self.my_object.owner_id:
			touch.ud['initial'] = touch.x
			print 'started sliding'

		# calls same function in it's ancestor
		Scatter.on_touch_down(self, touch)

	def on_touch_up (self, touch):
		# calls same function in it's ancestor, and slides the workspace
		Scatter.on_touch_up(self, touch)
		if not 'markerid' in touch.profile:
			return
		hand_id = int(touch.fid / self.hand_gesture_offset)
		gesture_id = touch.fid % self.hand_gesture_offset
		self.canvas.clear()
		self.draw()

		"""
		"  starts sliding  "
		"""
		if ('initial' in touch.ud) and touch.ud['initial'] != None and self.object_moving and hand_id != self.my_object.owner_id and self.x <= 0 and ((-1*self.x) % self.single_width() == 0):
			print 'about to slide'
			current = self.current_workspace()
			if touch.ud['initial'] > touch.x:
				if abs(touch.ud['initial'] - touch.x) > self.slide_threshold:
					current = current + 1
					if current >= len(self.frames):
						current = len(self.frames) - 1
					else:
						self.workspace_slide_event()
			else:
				if abs(touch.ud['initial'] - touch.x) > self.slide_threshold:
					current = current - 1
					if current < 0:
						current = 0
					else:
						self.workspace_slide_event()
			self.slide(current)
			touch.ud['initial'] = None
		return False

	def on_touch_move (self, touch):
		# will not work with simple touch anymore
		if not 'markerid' in touch.profile:
			return
		hand_id = int(touch.fid / self.hand_gesture_offset)
		gesture_id = touch.fid % self.hand_gesture_offset

		if self.object_moving and hand_id == self.my_object.owner_id:
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
			"  highlighting target  "
			"""
			if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
				self.my_target.highlight(True)
			else:
				self.my_target.highlight(False)

			"""
			"  release  "
			"""
			if gesture_id == self.release_gesture and ((-1*self.x) % self.single_width() == 0):
				self.object_moving = False
				self.object_released_event()
				self.play_release_sound()
				"""
				"  collide  "
				"""
				if self.my_target.collide_point(touch.x-self.x, touch.y-self.y):
					self.object_collide_event()
					self.swap_object_target()
					self.play_collide_sound()

		"""
		"  show cursor  "
		"""
		if not self.object_moving or touch.ud != self.my_object.owner_id:
			Scatter.on_touch_move(self, touch)
			self.canvas.clear()
			self.draw()
			self.canvas.add(Color(0,0,0))
			self.canvas.add(Ellipse(pos=(touch.x-self.x, touch.y-self.y), size=(30,30)))

class WorkspaceApp(App):
	container = None

	def on_key_down(self, instance, code, *largs):
		if (code == 27):
			print 'exit at', time.strftime('%H:%M:%S %y/%m/%d', time.localtime())
		if (code == 101):
			self.container.go_to_object()

	def build(self):
		Window.bind(on_key_down=self.on_key_down)
		root = Widget()
		self.container = Container(ws_count=7)
		# here we add an instance of container to the window, ws_count shows number of workspaces we need
		root.add_widget(self.container)
		return root

def log_time_action(action):
	Logger.info('something: ' + action + ' @' + str(time.time()))

if __name__ in ('__main__', '__android__'):
	log_time_action('start')
	WorkspaceApp().run()
