from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder


# Define the AdminWindow class
class AdminWindow(BoxLayout):
    pass

# Load the kv file
Builder.load_file("Admin/Admin.kv")

# Define the App class
class AdminApp(App):
    def build(self):
        return AdminWindow()

# Run the app
if __name__ == "__main__":
    AdminApp().run()