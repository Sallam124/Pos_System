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
import requests
import cv2
from pyzbar.pyzbar import decode


Builder.load_file('Operator/Operator.kv')

class notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.7,.7)

class Operation_Window(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.images = [
            "C:/Users/salla/OneDrive/Desktop/Integrative Project/Integrative-Project/Barcodes/barcode_3.png.png",
            "C:/Users/salla/OneDrive/Desktop/Integrative Project/Integrative-Project/Barcodes/barcode_4.png.png",
            "C:/Users/salla/OneDrive/Desktop/Integrative Project/Integrative-Project/Barcodes/barcode_2.png.png"
        ]
        
        client = MongoClient("mongodb://localhost:27017/")
        self.db = client.Pos    
        self.stocks = self.db.stocks
        self.Purchase_Records = self.db.Purchase_Records
        
        self.notify = notify()
        self.barcode = None
        self.cart = []
        self.quantity = []
        self.total = 0.00
        Total = 0
        self.post_tax = 0
        self.pending_records = [] 
        self.pending_updates = [] 


        Clock.schedule_interval(self.is_connection_established, 1800)



    def decode_barcodes(self, image_path=None):
        # If no image path is provided, return an empty list
        if image_path is None:
            return []   
        else:
            image = cv2.imread(image_path)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            barcodes = decode(gray_image)    
            return barcodes

    def decode_and_fetch_product(self, image_path=None):
        # If no image path is provided, return None
        if image_path is None:
            return None
            # Decode barcodes in the image
        barcodes = self.decode_barcodes(image_path) 
        # Assuming barcodes is a list of barcode objects
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")            
            
            return barcode_data

    def logout(self):
        self.parent.parent.current = 'Screen_sign'
    
    def killswitch(self,dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()
    
    def is_connection_established(self):
        try:
            requests.get("http://www.google.com", timeout=5)  # Increase timeout to 10 seconds
            print("Connection Established")
            return True
        except requests.ConnectionError:
            print("Connection Failed")
            return False
        
    def Connect(self):
        if self.Connection:
            online_client= MongoClient("mongodb+srv://sallamaym:BUY64iMKxpFcjp89@integrative.ic3wvml.mongodb.net/")
            self.online_db = online_client.Pos
            self.online_stocks = self.online_db.stocks
            return True
        else:
            return False
            

    def online_purchase_records(self,Record,column_name): # insert

        if self.Connect():
            online_collection = self.online_db[column_name]
            online_collection.insert_one(Record)
            print("Synchronization Successful")

        else:
            self.pending_records.append({'Record': Record, 'column_name': column_name})
            print("Data Appended, Will Sync After 30 minutes")
            print(self.pending_records)
            Clock.schedule_once(self.sync_pending_records,1800)



    def sync_to_online_database(self, product_code, column_name):

        if self.Connect():
            # Retrieve the existing document from online_stocks
            existing_record = self.online_stocks.find_one({"product_code": product_code})

            # Retrieve the value to update from the "stocks" collection
            record = self.stocks.find_one({"product_code": product_code})
            in_stock_value = record.get(column_name)

            # Update only the specified field in the existing document

            if existing_record:
                existing_record[column_name] = in_stock_value
                filter_query = {"product_code": product_code}
                # Use the existing document as the update query
                self.online_stocks.replace_one(filter_query, existing_record)
            else:
                # If the document doesn't exist, create a new one
                update_query = {"product_code": product_code, column_name: in_stock_value}
                self.online_stocks.insert_one(update_query)

            print("Synchronization Successful")
        else:
            print("Failed to sync local changes to online database:")
            print("Data Will be Updated After 30 Minutes")

            Clock.schedule_once(lambda dt: self.sync_to_online_database(product_code, column_name), 1800)


    
    def sync_pending_records(self):
        if self.is_connection_established():
            for record in self.pending_records:
                self.online_purchase_records(record["purchase_Record"], record["Purhcase_Records"])
            self.pending_records.clear()  # Remove the comma here

    
    def barcodes(self):
        barcode = None
        # Initialize barcode variable
        if self.images :  # Check if there are images left in the list
            image = self.images.pop(0)  # Get the first image path and remove it from the list
            barcode = self.decode_and_fetch_product(image)
            return barcode
 
    def on_barcode_button_pressed(self):
        barcode = self.barcodes()
        self.update_purchase(barcode)

    def update_purchase(self,barcode):
        
        if barcode:
            pcode = barcode
            self.ids.productcode.text = str(barcode)
            pcode = self.ids.productcode.text

        pcode = self.ids.productcode.text

        products_container = self.ids.products
        last_record = self.db.Purchase_Records.find_one(sort=[('receipt_number', -1)])  
        receipt = last_record['receipt_number']
        product_quantity = 0
        reciept_number = int(receipt[1:]) + 1

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
    
            Total_Quantity = self.ids.quantity.text
            

            if Total_Quantity == '' :
                Total_Quantity = 1
            else:
                Total_Quantity = int(Total_Quantity)
            total_price = Total_Quantity * product_price * 1.15  

            code = Label(text=pcode, size_hint_y=.7, size_hint_x=.1, color=get_color_from_hex('#111212'))
            name = Label(text=target_code['product_name'] , size_hint_y=.7, size_hint_x=.3, color=get_color_from_hex('#111212'))
            quantity = Label(text=str(Total_Quantity), size_hint_y=.7, size_hint_x=.1, color=get_color_from_hex('#111212'))
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
            
            self.total += pro_price * Total_Quantity
            self.total = round(self.total,2) 

            Discount = self.total * .02
            Discount = round(Discount,2)
            vat = self.total * .15
            vat = round(vat,2)
            
            self.post_tax =  (self.total* 1.15) - Discount
            self.post_tax = round(self.post_tax,2)
            
            purchase_Total = (
                '\n\nSubTotal:\t\t\t\t\t\t\t\t\t\t\t\t\t\t{:10}'.format(self.total)
                + '\nDiscount:\t\t\t\t\t\t\t\t\t\t\t\t\t\t-{:10}'.format(Discount)
                + '\nVat:\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{:10}'.format(vat)
                + '\nTotal:\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{:10}'.format(self.post_tax)
                + '\n\t'
            )


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

                self.quantity[i] += Total_Quantity
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
                self.quantity.append(Total_Quantity)
            
                # Construct a new line for the product in the receipt text
                new_text = ''.join([previous , pro_name + ':  \t\t\tx' + str(Total_Quantity) + '\t\t\t\t\t' + str(pro_price),'\t\t\t ',str(Total), purchase_Total])
                # Update the receipt text with the new line
                preview.text = new_text 

            self.ids.discount.text = '0.00'
            self.ids.quantity.text = str(Total_Quantity)
            self.ids.price.text = str(pro_price)
            self.ids.vat.text = '15%'
            self.ids.total.text = str(total_price)
            self.ids.productcode.text = ''
    

    def reset_order(self):
        # Reset order details
        self.ids.product.text = ''
        self.ids.cur_price.text = '0.00'
        self.ids.reciept_preview.text = 'Super Serve \n123 Banafseg \nThe 5th Settlement Space\nTel:(20)10-2928-4678 \nDate: 4/16/2024 \n\n'
        self.ids.discount.text = '0.00'
        self.ids.quantity.text = ''
        self.ids.price.text = '0.00'
        self.ids.vat.text = '15%'
        self.ids.total.text = '0.00'
        # Clear product details from the layout
        self.ids.products.clear_widgets()


    def update_database(self):
        # Deduct and update products in the database
        self.Connection = self.is_connection_established()
        for item, quantity in zip(self.cart, self.quantity):
            target_code = self.stocks.find_one({'product_code': item})
            if target_code:
                current_quantity = int(target_code.get('in_stock', 0))
                new_quantity = current_quantity - quantity
                purchase_date = datetime.now()
              
                current_sold = int(target_code.get('sold', 0))
                current_sold += quantity

                # Update the quantity in the database

                # Insert a new record for the transaction
                receipt_number = self.generate_receipt_number()  # Generate a new receipt number
                total_amount = self.total
                items_purchased = [{'product_code': item, 'quantity': quantity} for item, quantity in zip(self.cart, self.quantity)]

                purchase_record = {
                    'receipt_number': receipt_number,
                    'total': total_amount,
                    'last_purchase': purchase_date,
                    'items_purchased': items_purchased
                }
                self.reset_order()
                self.stocks.update_one({'product_code': item}, {'$set': {'in_stock': new_quantity}})
                self.stocks.update_one({'product_code': item}, {'$set': {'sold': current_sold}})
                self.db.Purchase_Records.insert_one(purchase_record)
                # Online
                self.sync_to_online_database(item,'in_stock')
                self.sync_to_online_database(item,'sold')
                self.online_purchase_records(purchase_record,"Purchase_Records")



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
    


class OperatorApp(App):
    def build(self):
        return Operation_Window()
        
if __name__ == "__main__":
    start = OperatorApp()
    start.run()