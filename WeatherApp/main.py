from __future__ import print_function
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.checkbox import CheckBox 
from kivy.properties import ObjectProperty, ListProperty
from kivy.network.urlrequest import UrlRequest 
import json
from kivy.uix.listview import ListItemButton
from kivy.factory import Factory

API_KEY = "ebdb10f67989131d05caadb1d21f7754"	# You should get your own

class WeatherRoot(BoxLayout):
	current_weather = ObjectProperty()
	def show_current_weather(self, location=None):
		
		self.clear_widgets()
		if location == None and self.current_weather is None:
			location = "New York (US)"
		if location is not None:
			self.current_weather = Factory.CurrentWeather() # Dynamic class defined in weather.kv file
			self.current_weather.location = location
		self.add_widget(self.current_weather)
		

	def show_add_location_form(self):
		self.clear_widgets()
		self.add_widget(AddLocationForm())	

class LocationButton(ListItemButton):
	location = LocationProperty()
	
	
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

class WeatherApp(App):
	pass

if __name__ == '__main__':
	WeatherApp().run()