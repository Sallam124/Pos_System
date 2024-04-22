from kivy.app import App 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import re
from kivy.uix.modalview import ModalView
from pymongo import MongoClient
from kivy.lang import Builder
from datetime import datetime

Builder.load_file('Operator/Operator.kv')

class notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.7,.7)

class Operation_Window(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        try:
            
            client = MongoClient("mongodb+srv://sallamaym:BUY64iMKxpFcjp89@integrative.ic3wvml.mongodb.net/")
            self.db = client.Pos    
            self.stocks = self.db.stocks
            self.Purchase_Records = self.db.Purchase_Records
        except Exception as e:
            print("Failed to connect to online database. Using local MongoDB instance.")

            client = MongoClient()
        self.db = client.Pos    
        self.stocks = self.db.stocks
        self.notify = notify()
        self.Purchase_Records = self.db.Purchase_Records
        self.cart = []
        self.quantity = []
        self.total = 0.00
        Total = 0
        self.post_tax = 0
        
    def logout(self):
        self.parent.parent.current = 'Screen_sign'
    
    def killswitch(self,dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()


        
        
    def update_purchase(self):  
        pcode = self.ids.productcode.text
        products_container = self.ids.products
        last_record = self.db.Purchase_Records.find_one(sort=[('receipt_number', -1)])  
        receipt = last_record['receipt_number']
        product_quantity = 0
        reciept_number = int(receipt[1:]) + 1

        #Verifying product code entered exists in our database
        target_code = self.stocks.find_one({'product_code': pcode})
        if target_code is None:
            self.notify.add_widget(Label(text='[color=#FFFFFF][b]Product not found![/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1) 
        else:
            # Create a new layout to hold the details of the product that is being added 
            details = BoxLayout(size_hint_y=None, height=30, pos_hint={'top': 1})
            products_container.add_widget(details)
        
            product_price = float(target_code.get('product_price', 0))
           
            Quantity = self.ids.quantity.text
            pcode = self.ids.productcode.text
            if Quantity == '' :
                Quantity = 1
            else:
                Quantity = int(Quantity)
            total_price = Quantity * product_price * 1.15  

            code = Label(text=pcode, size_hint_y=.7, size_hint_x=.1, color=get_color_from_hex('#111212'))
            name = Label(text=target_code['product_name'] , size_hint_y=.7, size_hint_x=.3, color=get_color_from_hex('#111212'))
            quantity = Label(text=str(Quantity), size_hint_y=.7, size_hint_x=.1, color=get_color_from_hex('#111212'))
            discount = Label(text='0.00%', size_hint_y=.7, size_hint_x=.1, color=get_color_from_hex('#111212'))
            price = Label(text=str(target_code['product_price']), size_hint_y=0.7, size_hint_x=0.1, color=get_color_from_hex('#111212'))
            vat = Label(text='15%', size_hint=(0.1, 0.7), color=get_color_from_hex('#111212'))
            total = Label(text="{:.3f}".format(total_price).rstrip('0').rstrip('.'), size_hint_y=.7, size_hint_x=.2, color=get_color_from_hex('#111212'))
            
            details.add_widget(code)
            details.add_widget(name)
            details.add_widget(quantity)
            details.add_widget(discount)
            details.add_widget(price)
            details.add_widget(vat)
            details.add_widget(total)
            
            
            pro_name = name.text 
            
            index = 0
            pro_price = float(price.text)

                
            product_quantity += int(quantity.text) 
                    
            Total = pro_price * product_quantity 
            
            self.total += pro_price * Quantity
            self.total = round(self.total,2) 
            
            vat = self.total * .15
            vat = round(vat,2)
            
            self.post_tax =  self.total* 1.15
            self.post_tax = round(self.post_tax,2)
            
            purchase_Total = '\n\nSubTotal:\t\t\t\t\t\t\t\t\t\t\t\t\t\t ' + str(self.total) +'\nVat:\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t'+ str(vat)+'\nTotal:\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t '+ str(self.post_tax) + '\n\t' 
            self.ids.product.text = pro_name
            self.ids.cur_price.text = str(pro_price)

            # Get the receipt preview widget and its current text
            preview = self.ids.reciept_preview 
            previous = preview.text  
            prev = previous.find('SubTotal')
            
            # Update reciept
            if prev > 0:
                previous = previous[:prev] # deletes any text found before prev , to print out updated reciept 
                
        
            found_product = False
            for i, code in enumerate(self.cart):
                if code == pcode:
                    found_product = True

                    
            if found_product:

                self.quantity[i] += Quantity
                product_quantity = self.quantity[i]
                Total = pro_price * product_quantity
                Total = round(Total,2)
            
                find_ = r'%s:\s+x\d+\s+\d+\.\d+\s+\d+\.\d+' % re.escape(pro_name)
                
                replace_ = '%s: \t\t\t\tx%d\t\t\t\t\t%.2f\t\t\t %.2f' % (pro_name, product_quantity, pro_price, Total)
                # Replace the existing product line in the receipt text with the updated line
                new_text = re.sub(find_, replace_, previous) 
                preview.text = new_text + purchase_Total.replace('\n','',2)
                #new line
            else:
                self.cart.append(pcode)
                self.quantity.append(Quantity)

                # Construct a new line for the product in the receipt text
                new_text = ''.join([previous , pro_name + '  \t\t\t\t\tx' + str(Quantity) + '\t\t\t\t\t' + str(pro_price),'\t\t\t ',str(Total), purchase_Total])
                # Update the receipt text with the new line
                preview.text = new_text

            self.ids.discount.text = '0.00'
            self.ids.quantity.text = ''
            self.ids.price.text = str(pro_price)
            self.ids.vat.text = '15%'
            self.ids.total.text = str(total_price)
            
    def update_database(self):
        # Deduct and update products in the database
        for item, quantity in zip(self.cart, self.quantity):
            target_code = self.stocks.find_one({'product_code': item})
            if target_code:
                current_quantity = int(target_code.get('in_stock', 0))  
                new_quantity = current_quantity - quantity
                
                current_sold = int(target_code.get('sold', 0))
                current_sold += quantity

                # Update the quantity in the database
                self.stocks.update_one({'product_code': item}, {'$set': {'in_stock': new_quantity}})
                self.stocks.update_many({'product_code': item}, {'$set': {'sold': current_sold}})
        
                # Insert a new record for the transaction
                receipt_number = self.generate_receipt_number()  # Generate a new receipt number
                total_amount = self.total
                purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M")

                items_purchased = [{'product_code': item, 'quantity': quantity} for item, quantity in zip(self.cart, self.quantity)]

                purchase_record = {
                    'receipt_number': receipt_number,
                    'total': total_amount,
                    'date': purchase_date,
                    'items_purchased': items_purchased
                }

                # Insert the record into the database
                
                self.db.Purchase_Records.insert_one(purchase_record)

            # After deduction, clear the cart and quantity list
            self.cart.clear()
            self.quantity.clear()
            # Reset the total
            self.total = 0.00

    def generate_receipt_number(self):
        last_record = self.db.Purchase_Records.find_one(sort=[('receipt_number', -1)])
        if last_record:
            last_receipt_number = last_record['receipt_number']
            # Extract the numeric part of the receipt number
            last_number = int(last_receipt_number[1:])
            # Increment the last number by 1
            new_number = last_number + 1
            # Construct the new receipt number
            new_receipt_number = "R{:06d}".format(new_number)


        return new_receipt_number
    
    def reset_order(self):
        # Reset order details
        self.ids.product.text = 'Default Product'
        self.ids.cur_price.text = '0.00'
        self.ids.reciept_preview.text = 'Super Serve \n123 Banafseg \nThe 5th Settlement Space\nTel:(20)10-2928-4678 \nDate: 4/16/2024 \n\n'
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