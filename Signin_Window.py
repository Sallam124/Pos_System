from kivy.logger import Logger
Logger.debug("Debug message")
Logger.info("Info message")
Logger.warning("Warning message")
Logger.error("Error message")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class Signin_Window(BoxLayout):
    pass

class Signin_app(App):
    def build(self):
        return Signin_Window()

if __name__ == "__main__":
    start = Signin_app()
    start.run()  