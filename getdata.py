from flask import Flask, jsonify
from pymongo import MongoClient 
from bson.json_util import dumps
from collections import defaultdict
import certifi
import json

app = Flask(__name__)

# Connect to MongoDB
try: 
	conn = MongoClient("mongodb+srv://dbUser:pEzoIQqV08S6JhpC@cluster0.tylwn63.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", tlsCAFile=certifi.where())
	print("Connected successfully!!!") 
except: 
	print("Could not connect to MongoDB") 
     
# database name: mydatabase 
db = conn.swa_address_search_engine 

# Created or Switched to collection names: myTable 
collection = db.address_collection      

@app.route('/api/data', methods=['GET'])
def get_data():
    # Query MongoDB to fetch data
    data = collection.find()

    # Initialize the list to store the final JSON structure
    json_data = []

    # Initialize a dictionary to group states by country
    country_states = {}

    # Process data from MongoDB
    for document in data:
        country = document.get("country", "")  # Get country, default to empty string if missing
        state = document.get("state", "")  # Get state, default to empty string if missing
        city = document.get("city", "")  # Get city, default to empty string if missing

        if not country or not state or not city:
            continue

        # Initialize the dictionary for the country if it doesn't exist
        if country not in country_states:
            country_states[country] = {"country": country, "states": []}

        # Find or create the dictionary for the state
        state_dict = next((item for item in country_states[country]["states"] if item["state"] == state), None)
        if state_dict is None:
            state_dict = {"state": state, "cities": []}
            country_states[country]["states"].append(state_dict)

        # Add the city to the state dictionary
        state_dict["cities"].append(city)

    # Convert the country_states dictionary to a list
    for country, data in country_states.items():
        json_data.append(data)

    return jsonify(json_data)

if __name__ == '__main__':
    app.run(debug=True)
