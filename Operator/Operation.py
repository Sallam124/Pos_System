from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class Operation_Window(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
class OperatorApp(App):
    def build(self):
        return Operation_Window()
        
if __name__ == "__main__":
    start = OperatorApp()
    start.run()