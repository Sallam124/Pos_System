from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.dropdown import DropDown

# Define the AdminWindow class
class AdminWindow(BoxLayout):
    pass

# Define the App class
class AdminApp(App):
    def build(self):
        return AdminWindow()

# Run the app
if __name__ == "__main__":
    AdminApp().run()
