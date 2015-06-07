from __future__ import print_function
from kivy.uix.scatter import Scatter 
from kivy.uix.label import Label 
from kivy.uix.floatlayout import FloatLayout 
from kivy.uix.textinput import TextInput 
from kivy.uix.boxlayout import BoxLayout 


from kivy.app import App

__version__ = '1.0.1'




class TutorialApp(App):
	
	def on_text(self, instance, value):

		print("Instance: {}\nValue: {}".format(instance, value))

	def build(self):
		b = BoxLayout(orientation='vertical')
		t = TextInput(size_hint_y=None,
					  font_size=150,
					  text='default',
					  height=200)	

		f = FloatLayout()
		s = Scatter()
		l = Label(text='Hello',
				  font_size=150)
		f.add_widget(s)
		s.add_widget(l)

		# Add text widget first so that it appears
		# on top of floatlayout
		b.add_widget(t)
		b.add_widget(f)
		t.bind(text=l.setter('text'))
		t.bind(text=lambda x,y: print(y))
		

		return b

if __name__ == '__main__':
	TutorialApp().run()