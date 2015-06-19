
from __future__ import print_function

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.checkbox import CheckBox 
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.network.urlrequest import UrlRequest 
from kivy.factory import Factory
import json
from kivy.uix.listview import ListItemButton
import random
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock


API_KEY = "ebdb10f67989131d05caadb1d21f7754"	# You should get your own

class WeatherRoot(BoxLayout):
	current_weather = ObjectProperty()
	def show_current_weather(self, location=None):
		
		self.clear_widgets()
		if self.current_weather is None:
			self.current_weather = CurrentWeather()
		if location is not None:
			self.current_weather.location = location
		self.current_weather.update_weather()	
		self.add_widget(self.current_weather)
		

	def show_add_location_form(self):
		self.clear_widgets()
		self.add_widget(AddLocationForm())	

class LocationButton(ListItemButton):
	location = ListProperty()
	
	
class AddLocationForm(BoxLayout):
	search_input = ObjectProperty()	#Property of text box
	search_results = ObjectProperty()
	check_box = ObjectProperty()

	def search_location(self):
		''' TODO Harden this method eventually '''
		print(self.check_box.active)
		global API_KEY

		search_template = "http://api.openweathermap.org/data/2.5/" + \
		"find?q={}&type=like&APPID=" + API_KEY

		search_url = search_template.format(self.search_input.text)

		request = UrlRequest(search_url, self.found_location,
							 on_error=self.received_error,
							 on_failure=self.received_failure)		# The second parameter is the response method

		print("User searched for {}".format(self.search_input.text))

	def found_location(self, request, data):

		data = json.loads(data.decode()) if not isinstance(data, dict) else data
		# changed strings to tuples
		cities = [(d['name'], d['sys']['country']) for d in data['list']]
		#And now we will update our list
		self.search_results.item_strings = cities
		#self.search_results.adapter.data.clear() Introduced only in python 3
		del self.search_results.adapter.data[:]
		self.search_results.adapter.data.extend(cities)
		self.search_results._trigger_reset_populate()

	def args_converter(self, index, data_item):
		city, country = data_item
		return {'location' : (city, country)}

	def received_error(self, request, error):
		print("Received an error: {}".format(error))
		
	def received_failure(self, request, result):
		print("Failure: {}\nResult type: {}".format(result, type(result)))


class CurrentWeather(BoxLayout):
	location = ListProperty(['New York', 'US'])
	conditions = ObjectProperty()
	temp = NumericProperty()
	hi_temp = NumericProperty()
	low_temp = NumericProperty()

	def update_weather(self):
		weather_template = "http://api.openweathermap.org/data/2.5/"+\
		"weather?q={},{}&units=metric&APPID=" + API_KEY
		weather_url = weather_template.format(*self.location) # Unpacking tuple / list with *
		request = UrlRequest(weather_url, self.weather_retrieved)

	def weather_retrieved(self, request, data):
		data = json.loads(data.decode()) if not isinstance(data, dict) else data
		#self.conditions = data['weather'][0]['description']
		self.render_conditions(data['weather'][0]['description'])
		self.temp = data['main']['temp']
		self.hi_temp = data['main']['temp_max']
		self.low_temp = data['main']['temp_min']
		print(data)		
		print("temp: {}\nhi: {}\nlow: {}".format(self.temp, self.hi_temp, self.low_temp))
	
	def render_conditions(self, conditions_description):
		if "clear" in conditions_description.lower():
			conditions_widget = Factory.ClearConditions()
		elif "snow" in conditions_description.lower():
			conditions_widget = Factory.SnowConditions()
		else:
			conditions_widget = Factory.UnknownConditions()
		conditions_widget.conditions = conditions_description
		self.conditions.clear_widgets()	# references the BoxLayout with id: conditions
		self.conditions.add_widget(conditions_widget)

class Conditions(BoxLayout):
	conditions = StringProperty()

class SnowConditions(Conditions):
	FLAKE_SIZE = 5
	NUM_FLAKES = 60
	FLAKE_AREA = FLAKE_SIZE * NUM_FLAKES
	FLAKE_INTERVAL = 1.0 / 30.0 # Update twice a second

	def __init__(self, **kwargs):
		super(SnowConditions, self).__init__(**kwargs)
		self.flakes = [[x * self.FLAKE_SIZE, 0]
			for x in range(self.NUM_FLAKES)]
		Clock.schedule_interval(self.update_flakes, self.FLAKE_INTERVAL)

	def update_flakes(self, time):
		for f in self.flakes:
			f[0] += random.choice([-1,1])
			f[1] -= random.randint(0, self.FLAKE_SIZE)
			if f[1] <= 0:
				f[1] = random.randint(0, int(self.height))

		self.canvas.before.clear()
		with self.canvas.before:
			widget_x = self.center_x - self.FLAKE_AREA / 2
			widget_y = self.pos[1]
			for x_flake, y_flake in self.flakes:
				x = widget_x + x_flake
				y = widget_y + y_flake
				Color(0.9, 0.9, 1.0)
				Ellipse(pos=(x,y), size=(self.FLAKE_SIZE, self.FLAKE_SIZE))




class WeatherApp(App):
	pass

if __name__ == '__main__':
	WeatherApp().run()