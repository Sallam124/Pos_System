from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

class Operation_Window(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def update_purchase(self):  
        code = self.ids.productcode.text
        products_container = self.ids.products
        
        if code == '1234':
            details = BoxLayout(size_hint_y= None,height=30,pos_hint={'top': 1})
            products_container.add_widget(details)
            
            code = Label(text=code , size_hint_x = .2 , color = get_color_from_hex('#43eb34'))
            name = Label(text='Product One' , size_hint_x = .6, color = get_color_from_hex('#43eb34'))
            quantity = Label(text='1', size_hint_x = .3, color = get_color_from_hex('#43eb34'))
            discount = Label(text='0.00' , size_hint_x = .2, color = get_color_from_hex('#43eb34'))
            price = Label(text= '0.00' , size_hint_x = .2, color = get_color_from_hex('#43eb34'))
            total = Label(text= '0.00', size_hint_x = .2, color = get_color_from_hex('#43eb34') )
            details.add_widget(code)
            details.add_widget(name)
            details.add_widget(quantity)
            details.add_widget(discount)
            details.add_widget(price)
            details.add_widget(total)


class OperatorApp(App):
    def build(self):
        return Operation_Window()
        
if __name__ == "__main__":
    start = OperatorApp()
    start.run()
