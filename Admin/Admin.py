from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from collections import OrderedDict
from pymongo import MongoClient
from Admin.Utilities.data import DataTable
from datetime import datetime
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg as mtp

Builder.load_file('Admin/Admin.kv')  # Load Kivy language file

# Custom modal view for notifications
class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.7,.7)

# Main application window
class AdminWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

        client_local = MongoClient()
        self.db = client_local.Pos    
        self.products = self.db.stocks
        self.Purchase_Records = self.db.Purchase_Records
        
        self.client_online = MongoClient("mongodb+srv://sallamaym:BUY64iMKxpFcjp89@integrative.ic3wvml.mongodb.net/")
        self.online_db = self.client_online.Pos
        self.online_products = self.online_db.stocks
        self.online_purchase_records = self.online_db.Purchase_Records
        


        self.notify = Notify()  # Notification modal instance

        # Populate product Spinner with data from database
        product_code = []
        product_name = []
        spinvals = []
        for product in self.products.find():
            product_code.append(product['product_code'])
            name = product['product_name']
            if len(name) > 30:
                name = name[:30] + '...'
            product_name.append(name)

        for x in range(len(product_code)):
            line = ' | '.join([product_code[x],product_name[x]])
            spinvals.append(line)
        self.ids.target_product.values = spinvals

        # Display user table
        content = self.ids.scrn_contents
        users = self.get_users()
        userstable = DataTable(table=users)
        content.add_widget(userstable)

        # Display product table
        product_scrn = self.ids.scrn_product_contents
        products = self.get_products()
        prod_table = DataTable(table=products)
        product_scrn.add_widget(prod_table)

    # Method to log out the user
    def logout(self):
        self.parent.parent.current = 'Screen_sign'
        
    # Method to add input fields for adding a new user
    def add_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name',multiline=False)
        crud_last = TextInput(hint_text='Last Name',multiline=False)
        crud_user = TextInput(hint_text='User Name',multiline=False)
        crud_pwd = TextInput(hint_text='Password',multiline=False)
        crud_des = Spinner(text='Operator',values=['Operator','Administrator'])
        crud_submit = Button(text='Add',size_hint_x=None,width=100,on_release=lambda x: self.add_user(crud_first.text,crud_last.text,crud_user.text,crud_pwd.text,crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)
    
    # Method to add a new user to the database
    def add_user(self, first,last,user,pwd,des):
        pwd = hashlib.sha256(pwd.encode()).hexdigest()  # Hash the password
        if first == '' or last == '' or user == '' or pwd == '':
            # Display notification if any required field is empty
            self.notify.add_widget(Label(text='[color=#FFFFFF][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch,1)
        else:
            # Insert new user data into the database
            self.users.insert_one({'first_name':first,'last_name':last,
        'user_name':user,'password':pwd,'designation':des,'date':datetime.now()})
            
            content = self.ids.scrn_contents

            content.clear_widgets()

            # Update user table
            users = self.get_users()
            userstable = DataTable(table=users)
            content.add_widget(userstable)
    
    # Method to dismiss notification modal and clear its widgets
    def killswitch(self,dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()

    # Method to add input fields for adding a new product
    def add_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        crud_code = TextInput(hint_text='Product Code',multiline=False)
        crud_name = TextInput(hint_text='Product Name',multiline=False)
        crud_weight = TextInput(hint_text='Product Weight',multiline=False)
        crud_stock = TextInput(hint_text='Product In Stock',multiline=False)
        crud_sold = TextInput(hint_text='Products Sold',multiline=False)
        crud_price = TextInput(hint_text='Product Price',multiline=False)
        crud_purchase = TextInput(hint_text='Last Purchase',multiline=False)
        crud_submit = Button(text='Add',size_hint_x=None,width=100,on_release=lambda x: self.add_product(crud_code.text,crud_name.text,crud_weight.text,crud_stock.text,crud_sold.text,crud_price.text,crud_purchase.text))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_weight)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(crud_price)
        target.add_widget(crud_purchase)
        target.add_widget(crud_submit)
    
    # Method to add a new product to the database
    def add_product(self,code,name,weight,stock,sold,price,purchase):
        if code == '' or name == '' or weight == '' or stock == '' or price == '': 
            # Display notification if any required field is empty
            self.notify.add_widget(Label(text='[color=#FFFFFF][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch,1)
        else:
            # Insert new product data into the database
            self.products.insert_one({'product_code':code,'product_name':name,'product_weight':weight,'in_stock':stock,'sold':sold,'product_price':price,'last_purchase':purchase})
            self.online_products.insert_one({'product_code':code,'product_name':name,'product_weight':weight,'in_stock':stock,'sold':sold,'product_price':price,'last_purchase':purchase})
            content = self.ids.scrn_product_contents
            content.clear_widgets()

            # Update product table
            prodz = self.get_products()
            stocktable = DataTable(table=prodz)
            content.add_widget(stocktable)
    
    # Method to update input fields for updating a user
    def update_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_first = TextInput(hint_text='First Name',multiline=False)
        crud_last = TextInput(hint_text='Last Name',multiline=False)
        crud_user = TextInput(hint_text='User Name',multiline=False)
        crud_pwd = TextInput(hint_text='Password',multiline=False)
        crud_des = Spinner(text='Operator',values=['Operator','Administrator'])
        crud_submit = Button(text='Update',size_hint_x=None,width=100,on_release=lambda x: self.update_user(crud_first.text,crud_last.text,crud_user.text,crud_pwd.text,crud_des.text))

        target.add_widget(crud_first)
        target.add_widget(crud_last)
        target.add_widget(crud_user)
        target.add_widget(crud_pwd)
        target.add_widget(crud_des)
        target.add_widget(crud_submit)
    
    # Method to update a user in the database
    def update_user(self, first,last,user,pwd,des):
        pwd = hashlib.sha256(pwd.encode()).hexdigest()  # Hash the password
        if user == '':
            # Display notification if username is empty
            self.notify.add_widget(Label(text='[color=#FFFFFF][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch,1)
        else:
            user = self.users.find_one({'user_name':user})
            if user == None:
                # Display notification if username is invalid
                self.notify.add_widget(Label(text='[color=#FFFFFF][b]Invalid Username[/b][/color]',markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch,1)
            else:
                # Update user data in the database
                if first == '':
                    first = user['first_name']
                if last == '':
                    last = user['last_name']
                if pwd == '':
                    pwd = user['password']
                self.users.update_one({'user_name':user},{'$set':{'first_name':first,'last_name':last,'user_name':user,'password':pwd,'designation':des,'date':datetime.now()}})
                content = self.ids.scrn_contents
                content.clear_widgets()

                # Update user table
                users = self.get_users()
                userstable = DataTable(table=users)
                content.add_widget(userstable)

    # Method to update input fields for updating a product
    def update_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()

        crud_code = TextInput(hint_text='Product Code',multiline=False)
        crud_name = TextInput(hint_text='Product Name',multiline=False)
        crud_weight = TextInput(hint_text='Product Weight',multiline=False)
        crud_stock = TextInput(hint_text='Product In Stock',multiline=False)
        crud_sold = TextInput(hint_text='Products Sold',multiline=False)
        crud_price = TextInput(hint_text='Product Price',multiline=False)
        crud_purchase = TextInput(hint_text='Last Purchase',multiline=False)
        crud_submit = Button(text='Update',size_hint_x=None,width=100,on_release=lambda x: self.update_product(crud_code.text,crud_name.text,crud_weight.text,crud_stock.text,crud_sold.text,crud_price.text,crud_purchase.text))

        target.add_widget(crud_code)
        target.add_widget(crud_name)
        target.add_widget(crud_weight)
        target.add_widget(crud_stock)
        target.add_widget(crud_sold)
        target.add_widget(crud_price)
        target.add_widget(crud_purchase)
        target.add_widget(crud_submit)
    
    # Method to update a product in the database
    def update_product(self, code, name, weight, stock, sold, price, purchase):
        if code == '':
            # Display notification if product code is empty
            self.notify.add_widget(Label(text='[color=#FFFFFF][b]Code required[/b][/color]', markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch, 1)
        else:
            target_code = self.products.find_one({'product_code': code})
            if target_code is None:
                # Display notification if product code is invalid
                self.notify.add_widget(Label(text='[color=#FFFFFF][b]Invalid Code[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)
            else:
                # Update product data in the database
                if name == '':
                    name = target_code['product_name']
                if weight == '':
                    weight = target_code['product_weight']
                if stock == '':
                    stock = target_code['in_stock']
                if sold == '':
                    sold = target_code['sold']
                if price == '':
                    price = target_code['product_price']
                if purchase == '':
                    purchase = target_code['last_purchase']
                content = self.ids.scrn_product_contents
                content.clear_widgets()
                
                self.products.update_one({'product_code': code}, {'$set': {'product_code': code, 'product_name': name, 'product_weight': weight, 'in_stock': stock, 'sold': sold, 'product_price': price, 'last_purchase': purchase}})
                self.online_products.update_one({'product_code': code}, {'$set': {'product_code': code, 'product_name': name, 'product_weight': weight, 'in_stock': stock, 'sold': sold, 'product_price': price, 'last_purchase': purchase}})
                prodz = self.get_products()
                stocktable = DataTable(table=prodz)
                content.add_widget(stocktable)

    # Method to remove input fields for removing a user
    def remove_user_fields(self):
        target = self.ids.ops_fields
        target.clear_widgets()
        crud_user = TextInput(hint_text='User Name')
        crud_submit = Button(text='Remove',size_hint_x=None,width=100,on_release=lambda x: self.remove_user(crud_user.text))

        target.add_widget(crud_user)
        target.add_widget(crud_submit)
    
    # Method to remove input fields for removing a product
    def remove_product_fields(self):
        target = self.ids.ops_fields_p
        target.clear_widgets()
        crud_code = TextInput(hint_text='Product Code')
        crud_submit = Button(text='Remove',size_hint_x=None,width=100,on_release=lambda x: self.remove_product(crud_code.text))

        target.add_widget(crud_code)
        target.add_widget(crud_submit)

    # Method to remove a user from the database
    def remove_user(self,user):
        if user == '':
            # Display notification if username is empty
            self.notify.add_widget(Label(text='[color=#FFFFFF][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch,1)
        else:
            target_user = self.users.find_one({'user_name':user})
            if target_user == None:
                # Display notification if username is invalid
                self.notify.add_widget(Label(text='[color=#FFFFFF][b]Invalid UserName[/b][/color]',markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch,1)
            else:
                content = self.ids.scrn_contents
                content.clear_widgets()

                # Remove user from the database
                self.users.delete_one({'user_name':user})
                self.notify.add_widget(Label(text='[color=#00FF00][b]User removed successfully[/b][/color]', markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch, 1)

                # Update user table
                users = self.get_users()
                userstable = DataTable(table=users)
                content.add_widget(userstable)
    
    # Method to remove a product from the database
    def remove_product(self,code):
        if code == '':
            # Display notification if product code is empty
            self.notify.add_widget(Label(text='[color=#FFFFFF][b]All Fields Required[/b][/color]',markup=True))
            self.notify.open()
            Clock.schedule_once(self.killswitch,1)
        else:
            target_code = self.products.find_one({'product_code':code})
            if target_code == None:
                # Display notification if product code is invalid
                self.notify.add_widget(Label(text='[color=#FFFFFF][b]Invalid Code[/b][/color]',markup=True))
                self.notify.open()
                Clock.schedule_once(self.killswitch,1)
            else:
                content = self.ids.scrn_product_contents
                content.clear_widgets()

                # Remove product from the database
                self.products.delete_one({'product_code':code})
                self.online_products.delete_one({'product_code':code})
                # Update product table
                prodz = self.get_products()
                stocktable = DataTable(table=prodz)
                content.add_widget(stocktable)

    # Method to fetch users data from the database
    def get_users():
        # Offline database connection
        offline_client = MongoClient()
        offline_db = offline_client.Pos
        offline_users = offline_db.users

        # Online database connection
        online_client = MongoClient("mongodb+srv://sallamaym:BUY64iMKxpFcjp89@integrative.ic3wvml.mongodb.net/")
        online_db = online_client.Pos
        online_users = online_db.users

        _users = OrderedDict()

        # Initialize dictionaries for offline and online users
        _users['offline'] = OrderedDict()
        _users['online'] = OrderedDict()

        # Function to append user data into a dictionary
        def append_user_data(user_data, user_dict):
            for idx, user in enumerate(user_data):
                user_dict['first_names'][idx] = user['first_name']
                user_dict['last_names'][idx] = user['last_name']
                user_dict['user_names'][idx] = user['user_name']
                pwd = user['password']
                if len(pwd) > 10:
                    pwd = pwd[:10] + '...'
                user_dict['passwords'][idx] = pwd
                user_dict['designations'][idx] = user['designation']

        # Offline users data retrieval
        offline_user_data = list(offline_users.find())
        offline_users_length = len(offline_user_data)
        offline_user_dict = {
            'first_names': {},
            'last_names': {},
            'user_names': {},
            'passwords': {},
            'designations': {}
        }
        append_user_data(offline_user_data, offline_user_dict)

        # Online users data retrieval
        online_user_data = list(online_users.find())
        online_users_length = len(online_user_data)
        online_user_dict = {
            'first_names': {},
            'last_names': {},
            'user_names': {},
            'passwords': {},
            'designations': {}
        }
        append_user_data(online_user_data, online_user_dict)

        # Append offline and online user data into _users dictionary
        _users['offline'] = offline_user_dict
        _users['online'] = online_user_dict

        return _users

    # Example usage
    users_data = get_users()
    print(users_data)
    

    # Method to fetch products data from the database

    def get_products():
        # Offline database connection
        offline_client = MongoClient()
        offline_db = offline_client.Pos
        offline_products = offline_db.stocks

        # Online database connection
        online_client = MongoClient("mongodb+srv://sallamaym:BUY64iMKxpFcjp89@integrative.ic3wvml.mongodb.net/")
        online_db = online_client.Pos
        online_products = online_db.stocks

        _stocks = OrderedDict()

        # Initialize dictionaries for offline and online products
        _stocks['offline'] = OrderedDict()
        _stocks['online'] = OrderedDict()

        # Function to append product data into a dictionary
        def append_product_data(product_data, product_dict):
            for idx, product in enumerate(product_data):
                product_dict['product_code'][idx] = product['product_code']
                name = product['product_name']
                if len(name) > 10:
                    name = name[:10] + '...'
                product_dict['product_name'][idx] = name
                product_dict['product_weight'][idx] = product['product_weight']
                product_dict['in_stock'][idx] = product['in_stock']
                product_dict['sold'][idx] = product['sold']
                product_dict['product_price'][idx] = product['product_price']
                product_dict['last_purchase'][idx] = product['last_purchase']

        # Offline products data retrieval
        offline_product_data = list(offline_products.find())
        offline_products_length = len(offline_product_data)
        offline_product_dict = {
            'product_code': {},
            'product_name': {},
            'product_weight': {},
            'in_stock': {},
            'sold': {},
            'product_price': {},
            'last_purchase': {}
        }
        append_product_data(offline_product_data, offline_product_dict)

        # Online products data retrieval
        online_product_data = list(online_products.find())
        online_products_length = len(online_product_data)
        online_product_dict = {
            'product_code': {},
            'product_name': {},
            'product_weight': {},
            'in_stock': {},
            'sold': {},
            'product_price': {},
            'last_purchase': {}
        }
        append_product_data(online_product_data, online_product_dict)

        # Append offline and online product data into _stocks dictionary
        _stocks['offline'] = offline_product_dict
        _stocks['online'] = online_product_dict

        return _stocks

    # Example usage
    products_data = get_products()
    print(products_data)



    def view_stats(self):
        plt.cla()
        self.ids.analysis_res.clear_widgets()
        target_product = self.ids.target_product.text
        target = target_product[:target_product.find(' | ')]
        name = target_product[target_product.find(' | '):] 

        df = pd.read_csv("C:\\Users\\salla\\OneDrive\\Desktop\\Integrative Project\\Integrative-Project\\Admin\\products_purchase.csv")
        purchases = []
        dates = []
        count = 0
        for x in range(len(df)):
            if str(df.Product_Code[x]) == target:
                purchases.append(df.Purchased[x])
                dates.append(count)
                count+=1
        plt.bar(dates,purchases,color='teal',label=name)
        plt.ylabel('Total Purchases')
        plt.xlabel('day')

        self.ids.analysis_res.add_widget(mtp(plt.gcf()))


    def change_screen(self, instance):
        if instance.text == 'Manage Products':
            self.ids.scrn_mngr.current = 'scrn_product_content'
        elif instance.text == 'Manage Users':
            self.ids.scrn_mngr.current = 'scrn_content'
        else:
            self.ids.scrn_mngr.current = 'scrn_analysis'


class AdminApp(App):
    def build(self):
        return AdminWindow()

if __name__=='__main__':
    AdminApp().run()
