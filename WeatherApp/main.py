from __future__ import print_function
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout 
from kivy.properties import ObjectProperty
from kivy.network.urlrequest import UrlRequest 

API_KEY = "ebdb10f67989131d05caadb1d21f7754"	# You should get your own

class AddLocationForm(BoxLayout):
	search_input = ObjectProperty()	#Property of text box
	search_results = ObjectProperty()

	def search_location(self):
		global API_KEY
		search_template = "http://api.openweathermap.org/data/2.5/" + \
		"find?q={}&type=like&APPID=" + API_KEY
		search_url = search_template.format(self.search_input.text)

		request = UrlRequest(search_url, self.found_location,
							 on_error=self.received_error,
							 on_failure=self.received_failure)		# The second parameter is the response method
		print("User searched for {}".format(self.search_input.text))

	def found_location(self, request, data):
		cities = ["{} ({})".format(d['name'], d['sys']['country'])
			for d in data['list']]
		print("\n".join(cities))  # Make this current with new api
		#And now we will update our list
		self.search_results.item_strings = cities

	def received_error(self, request, error):
		print("Received an error: {}".format(error))
		
	def received_failure(self, request, result):
		print("Failure: {}\nResult type: {}".format(result, type(result)))

class WeatherApp(App):
	pass

if __name__ == '__main__':
	WeatherApp().run()