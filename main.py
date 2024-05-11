from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout

from Admin.Admin import AdminWindow
from Signin_Window.Signin_Window import Signin_Window
from Operator.Operation import Operation_Window

class MainWindow(BoxLayout):
    admin = AdminWindow()
    Signin = Signin_Window()
    Operation = Operation_Window()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.Screen_sign.add_widget(self.Signin)
        self.ids.Screen_admin.add_widget(self.admin)
        self.ids.Screen_Operation.add_widget(self.Operation)

class Mainapp(App):
    def build(self):

        return MainWindow() 
        
if __name__ == '__main__':      
    Mainapp().run()