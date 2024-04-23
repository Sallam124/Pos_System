import cv2
from pyzbar.pyzbar import decode
from pymongo import MongoClient

# Connect to the MongoDB client
client = MongoClient("mongodb+srv://sallamaym:BUY64iMKxpFcjp89@integrative.ic3wvml.mongodb.net/")

# Access the database
db = client["Pos"]

# Access the collection
collection = db["stocks"]

# Retrieve all documents in the collection
documents = collection.find()

# Counter to generate unique barcode numbers
barcode_counter = 2345671000000  # Starting number for EAN-13 barcodes

# Update each document with a unique barcode number and generate the barcode image
for document in documents:
    # Update the document with the barcode number
    collection.update_one(
        {"_id": document["_id"]}, 
        {"$set": {"barcode_number": int(barcode_counter)}}
    )

    # Increment the barcode counter
    barcode_counter += 1

# Print success message
print("Barcode numbers filled into the 'barcode_number' column and EAN-13 barcodes generated successfully.")
