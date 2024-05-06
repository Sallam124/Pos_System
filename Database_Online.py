from pymongo import MongoClient
import hashlib

client = MongoClient()

database = client["Pos"]

purchase_records_collection = database["Purchase_Records"]

filter_condition = {"receipt_number": {"$gt": "R000010"}}

result = purchase_records_collection.delete_many(filter_condition)

print("Number of documents deleted:", result.deleted_count)



