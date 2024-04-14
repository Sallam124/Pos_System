from pymongo import MongoClient
import hashlib

client = MongoClient()

database = client["Pos"]

users_collection = database["users"]

all_users = users_collection.find()

for user in all_users:
    username = user['user_name']
    password = user['password']  # No need to decode
    print(f"Username: {username}, Password: {password}")



new_user = {
    "first_name": "New",
    "last_name": "User",
    "user_name": "Admin0",
    "password": hashlib.sha256("Admin0".encode()).hexdigest(),  
    "designation": "Administrator",  
    "date": "2024-04-14"  
}
users_collection.insert_one(new_user)
print("New user added successfully!")
