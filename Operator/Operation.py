from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import re
from pymongo import MongoClient
from kivy.lang import Builder

# Builder.load_file('Operator/Operator.kv')

class Operation_Window(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        client = MongoClient()
        self.db = client.Pos    
        self.stocks = self.db.stocks

        self.cart = []
        self.quantity = []
        self.total = 0.00
        
    def logout(self):
        self.parent.parent.current = 'Screen_sign'

    def update_purchase(self):  
        
        pcode = self.ids.productcode.text # Get the product code entered by the user from kivy file
        products_container = self.ids.products # Get the container where product details will be displayed from kivy file

        target_code = self.stocks.find_one({'product_code':pcode})
        if target_code == None:
            pass 
        else:
            # Create a new layout to hold the details of the product that is being added 
            details = BoxLayout(size_hint_y= None,height=30,pos_hint={'top': 1})
            products_container.add_widget(details)
            product_price = target_code.get('product_price', 0)  # Accessing 'product_price' field from target_code, defaulting to 0 if not found
            product_price = float(product_price)  # Convert product_price to float
            Totall = product_price * 1.15
            

            code = Label(text=pcode ,size_hint_y= .7, size_hint_x = .1 , color = get_color_from_hex('#000000'))
        
            name = Label(text=target_code['product_name'] ,size_hint_y= .7, size_hint_x = .3, color = get_color_from_hex('#000000'))
        
            quantity = Label(text='1',size_hint_y= .7, size_hint_x = .1, color = get_color_from_hex('#000000'))
        
            discount = Label(text='0.00' ,size_hint_y= .7, size_hint_x = .1, color = get_color_from_hex('#000000'))
        
            price = Label(text=str(target_code['product_price']), size_hint_y=0.7, size_hint_x=0.1, color=get_color_from_hex('#000000'))

            total = Label(text= str(Totall),size_hint_y= .7, size_hint_x = .2, color = get_color_from_hex('#000000') )
        
            details.add_widget(code)
        
            details.add_widget(name)
        
            details.add_widget(quantity)
        
            details.add_widget(discount)
        
            details.add_widget(price)
        
            details.add_widget(total)


            pro_name = name.text

            pro_price = float(price.text)
            product_quantity_str = str('1')
            self.total += pro_price * 1.15
            purchase_Total = '\n\nTotal\t\t\t\t\t\t'+str(self.total)
            self.ids.product.text = pro_name
            self.ids.cur_price.text = str(pro_price)

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
                find_ = '%s\t\tx\d\t' % (pro_name)
                replace_ = pro_name + '\t\tx' + str(product_quantity_str) + '\t'
            # Replace the existing product quantity in the receipt text with the updated quantity
                new_text = re.sub(find_, replace_, previous)
                preview.text = new_text + purchase_Total.replace('\n','')
            else:
                self.cart.append(pcode)
                self.quantity.append(1)
            # Construct a new line for the product in the receipt text
                new_text = ''.join([previous, pro_name + '\t\tx' + str(product_quantity_str) + '\t\t' + str(pro_price),'\nVat: 15% \n', purchase_Total])
            # Update the receipt text with the new line
                preview.text = new_text 
            
            self.ids.discount.text = '0.00'
            self.ids.quantity.text = str(product_quantity_str)
            self.ids.price.text = str(pro_price)
            self.ids.vat.text = '15%'
            self.ids.total.text = str(pro_price)

    def update_database(self):
        # Deduct and update products in the database
        for item, quantity in zip(self.cart, self.quantity):
            target_code = self.stocks.find_one({'product_code': item})
            if target_code:
                current_quantity = target_code.get('in_stock',0)
                new_quantity = current_quantity - quantity
                
                current_sold = target_code.get('sold',0)
                print(current_sold)
                current_sold += quantity
                # Update the quantity in the database
                print(current_sold)

                self.stocks.update_one({'product_code': item}, {'$set': {'in_stock': new_quantity}})
                self.stocks.update_many({'product_code':item},{'$set': {'sold': current_sold}})
        # After deduction, clear the cart and quantity list
        self.cart.clear()
        self.quantity.clear()
        # Reset the total
        self.total = 0.00

    def reset_order(self):
        # Reset order details
        self.ids.product.text = 'Default Product'
        self.ids.cur_price.text = '0.00'
        self.ids.reciept_preview.text = 'Super Serve \n 123 Banafseg.\n The 5th Settlement.Space\n\nTel:(20)10-2928-4678 \nReciept Number: 0001 \n Date: 4/16/2024 \n\n'
        self.ids.discount.text = '0.00'
        self.ids.quantity.text = '0'
        self.ids.price.text = '0.00'
        self.ids.vat.text = '15%'
        self.ids.total.text = '0.00'
        # Clear product details from the layout
        self.ids.products.clear_widgets()

class OperatorApp(App):
    def build(self):
        return Operation_Window()
        
if __name__ == "__main__":
    start = OperatorApp()
    start.run()
