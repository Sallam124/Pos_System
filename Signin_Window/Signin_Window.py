import subprocess
from kivy.logger import Logger  
Logger.debug("Debug message")
Logger.info("Info message")
Logger.warning("Warning message")
Logger.error("Error message")
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from pymongo import MongoClient
import hashlib
import time
Builder.load_file('Signin_Window/Signin_app.kv')

class Signin_Window(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Initialize the parent class

    def validate(self):
        client = MongoClient()
        database = client.Pos
        users = database.users
        user_input = self.ids.username_field.text.strip()  # Get the entered username
        password_input = self.ids.pwd_field.text.strip()  # Get the entered password

        if user_input == '':
            self.ids.info.text = '[color=#FF0000]Username is required[/color]'  
        elif password_input == '':
            self.ids.info.text = '[color=#FF0000]Password is required[/color]'
        else:
            user = users.find_one({'user_name': user_input})
            if user == None:
                self.ids.info.text = '[color=#FF0000]Invalid Username[/color]'

            else:
                hashed_password = hashlib.sha256(password_input.encode()).hexdigest()
                if hashed_password == user['password']:
                    des = user['designation'] 
                    self.ids.info.text = '[color=#00FF00]Success[/color]'

                    self.parent.parent.parent.ids.Screen_Operation.children[0].ids.loggedin_user_button.text = user_input
                    if des == 'Administrator':
                        self.parent.parent.current = 'Screen_admin'
                    else:
                        self.parent.parent.current = 'Screen_Operation'
                else:
                    self.ids.info.text = '[color=#FF0000]Invalid Password[/color]' 
                    print(user['password'])
    


# class Signin_app(App): # use imported (App) to start the program
#     def build(self):
#         return Signin_Window() 

# if __name__ == "__main__":
#     start = Signin_app()  
#     start.run() 
