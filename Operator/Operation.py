from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import re


class Operation_Window(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        self.cart = []
        self.quantity = []

    def update_purchase(self):  
        
        pcode = self.ids.productcode.text # Get the product code entered by the user from kivy file
        products_container = self.ids.products # Get the container where product details will be displayed from kivy file
        
        if pcode == '1234':
            # Create a new layout to hold the details of the product that is being added 
            details = BoxLayout(size_hint_y= None,height=30,pos_hint={'top': 1})
            products_container.add_widget(details)
            
            code = Label(text=pcode ,size_hint_y= .7, size_hint_x = .1 , color = get_color_from_hex('#43eb34'))
        
            name = Label(text='Product One' ,size_hint_y= .7, size_hint_x = .3, color = get_color_from_hex('#43eb34'))
        
            quantity = Label(text='1',size_hint_y= .7, size_hint_x = .1, color = get_color_from_hex('#43eb34'))
        
            discount = Label(text='0.00' ,size_hint_y= .7, size_hint_x = .1, color = get_color_from_hex('#43eb34'))
        
            price = Label(text= '0.00' ,size_hint_y= .7, size_hint_x = .1, color = get_color_from_hex('#43eb34'))
        
            total = Label(text= '0.00',size_hint_y= .7, size_hint_x = .2, color = get_color_from_hex('#43eb34') )
        
            details.add_widget(code)
        
            details.add_widget(name)
        
            details.add_widget(quantity)
        
            details.add_widget(discount)
        
            details.add_widget(price)
        
            details.add_widget(total)


            pro_name = 'Product One'
            pro_price = 1.00
            product_quantity_str = str('1')
            purchase_Total = '\n\n  Total\t\t\t\t\t\t0.00'

            # Get the receipt preview widget and its current text
            preview = self.ids.reciept_preview
            previous = preview.text
            prev = previous.find('Total')

            # Update cart
            if prev > 0:

                previous = previous[:prev] # deletes any text found after prev , to print out updated reciept 

            
            found_product = False
            for i, code in enumerate(self.cart):        
                if code == pcode:
                    found_product = True

            if found_product:
                product_quantity_str = self.quantity[i] + 1
                self.quantity[i] = product_quantity_str

            # Construct expressions for finding and replacing the product quantity in the receipt text
                expr = '%s\t\tx\d\t' % (pro_name)
                rexpr = pro_name + '\t\tx' + str(product_quantity_str) + '\t'
            # Replace the existing product quantity in the receipt text with the updated quantity
                new_text = re.sub(expr, rexpr, previous)
                preview.text = new_text
            else:
                self.cart.append(pcode)
                self.quantity.append(1)
            # Construct a new line for the product in the receipt text
                new_text = '\n'.join([previous, pro_name + '\t\tx' + str(product_quantity_str) + '\t\t' + str(pro_price), purchase_Total])
            # Update the receipt text with the new line
                preview.text = new_text


class OperatorApp(App):
    def build(self):
        return Operation_Window()
        
if __name__ == "__main__":
    start = OperatorApp()
    start.run()
