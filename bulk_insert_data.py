import json
import os
import pymongo
import datetime

# connect to your Atlas cluster
client = pymongo.MongoClient('mongodb+srv://dbUser:pEzoIQqV08S6JhpC@cluster0.tylwn63.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

# Get the path to the JSON file in the same folder
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, 'data_india.json')
# create new documents
dataToInsert = []

# Read data from the JSON file
with open(file_path) as f:
    dataToInsert = json.load(f)

print('Length of data', len(dataToInsert));

# get the database and collection on which to run the operation
collection = client['swa_address_search_engine']['address_collection']

# insert documents
collection.insert_many(dataToInsert)

# find documents 
result = collection.count_documents({ "country": "India" })
print("Number of documents found:", result)
