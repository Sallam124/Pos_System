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

first_name = input("Enter first name: ")
last_name = input("Enter last name: ")
user_name = input("Enter username: ")
password = input("Enter password: ")
designation = input("Enter designation: ")
last_log = input("Enter last log date (YYYY-MM-DD): ")

hashed_password = hashlib.sha256(password.encode()).hexdigest()

new_user = {
    "first_name": first_name,
    "last_name": last_name,
    "user_name": user_name,
    "password": hashed_password,
    "designation": designation,
    "last_log": last_log
}
users_collection.insert_one(new_user)

if users_collection.inserted_id:
    print("New user inserted successfully.")
else:
    print("Failed to insert new user.")


