from kivy.logger import Logger  
Logger.debug("Debug message")
Logger.info("Info message")
Logger.warning("Warning message")
Logger.error("Error message")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import string

class Signin_Window(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Initialize the parent class

    def validate(self):
        user = self.ids.username_field  #username input widget
        pwd = self.ids.pwd_field  #password input widget
        info =self.ids.info

        name = user.text  # Get the entered username
        password = pwd.text  # Get the entered password
        name = name.strip()  # Remove spaces before and after the username
        password = password.strip()  # Remove spaces before and after the password

        if name == '':
            info.text= '[color=#FF0000]Username is required[/color]'  
        elif password == '':
            info.text ='[color=#FF0000]Password is required[/color]'  
        else:
            if name == 'admin' and password == 'admin':
                info.text= '[color=#00FF00]Success[/color]' 
            else:
                info.text ='[color=#FF0000]Invalid Username and/or Password[/color]' 


class Signin_app(App): # use imported (App) to start the program
    def build(self):
        return Signin_Window() 

if __name__ == "__main__":
    start = Signin_app()  
    start.run() 
