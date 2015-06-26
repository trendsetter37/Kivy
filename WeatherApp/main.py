
from __future__ import print_function
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.checkbox import CheckBox 
from kivy.properties import ObjectProperty, ListProperty, NumericProperty, StringProperty
from kivy.network.urlrequest import UrlRequest 
import json
from kivy.uix.listview import ListItemButton
from kivy.factory import Factory
from kivy.storage.jsonstore import JsonStore


API_KEY = "ebdb10f67989131d05caadb1d21f7754"	# You should get your own

def locations_args_converter( index, data_item):
		city, country = data_item
		return {'location' : (city, country)}

class WeatherRoot(BoxLayout):
	current_weather = ObjectProperty()
	locations = ObjectProperty()

	def __init__(self, **kwargs):
		super(WeatherRoot, self).__init__(**kwargs)
		self.store = JsonStore("weather_store.json")
		if self.store.exists("locations"):
			current_location = self.store.get("locations")['current_location']
			self.show_current_weather(current_location)


	def show_current_weather(self, location=None):		
		self.clear_widgets()
		if self.current_weather is None:
			self.current_weather = CurrentWeather()
		if self.locations is None:
			self.locations = Factory.Locations()
			if self.store.exists('locations'):
				locations = self.store.get("locations")['locations']
				self.locations.locations_list.adapter.data.extend(locations)
		if location is not None:
			self.current_weather.location = location
			if location not in self.locations.locations_list.adapter.data:
				self.locations.locations_list.adapter.data.append(location)
				self.locations.locations_list._trigger_reset_populate()
				self.store.put("locations", 
					locations=list(self.locations.locations_list.adapter.data),
					current_location = location)

		self.current_weather.update_weather()	
		self.add_widget(self.current_weather)
		

	def show_add_location_form(self):
		self.clear_widgets()
		self.add_widget(AddLocationForm())

		

	def show_locations(self):
		self.clear_widgets()
		self.add_widget(self.locations)

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

	'''def args_converter(self, index, data_item):
		city, country = data_item
		return {'location' : (city, country)}'''

	def received_error(self, request, error):
		print("Received an error: {}".format(error))
		
	def received_failure(self, request, result):
		print("Failure: {}\nResult type: {}".format(result, type(result)))


class CurrentWeather(BoxLayout):
	location = ListProperty(['New York', 'US'])
	conditions = StringProperty()
	conditions_image = StringProperty()
	temp = NumericProperty()
	hi_temp = NumericProperty()
	low_temp = NumericProperty()

	def update_weather(self):
		config = WeatherApp.get_running_app().config
		temp_type = config.getdefault("General", "temp_type", "metric").lower()

		weather_template = "http://api.openweathermap.org/data/2.5/"+\
		"weather?q={},{}&units={}&APPID=" + API_KEY
		weather_url = weather_template.format(self.location[0], self.location[1], temp_type) # Unpacking tuple / list with *
		request = UrlRequest(weather_url, self.weather_retrieved)

	def weather_retrieved(self, request, data):
		data = json.loads(data.decode()) if not isinstance(data, dict) else data
		self.conditions = data['weather'][0]['description']
		self.conditions_image = "http://openweathermap.org/img/w/{}.png".format(data['weather'][0]['icon'])
		self.temp = data['main']['temp']
		self.hi_temp = data['main']['temp_max']
		self.low_temp = data['main']['temp_min']
		print(data)
		print("temp: {}\nhi: {}\nlow: {}".format(self.temp, self.hi_temp, self.low_temp))


class WeatherApp(App):
	def build_config(self, config):
		config.setdefaults('General', {'temp_type':'Metric'})

	def build_settings(self, settings):
		settings.add_json_panel("Weather Settings", self.config, data="""
			[
				{"type":"options",
				 	"title":"Temperature System",
				 	"section":"General",
				 	"key":"temp_type",
				 	"options": ["Metric", "Imperial"]
				}
			]""")

	def on_config_change(self, config, section, key, value):
		if config is self.config and key == "temp_type":
			try:
				self.root.children[0].update_weather()
			except AttributeError:
				pass

	

if __name__ == '__main__':
	WeatherApp().run()