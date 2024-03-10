from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from pymongo import MongoClient 
from bson.json_util import dumps
from collections import defaultdict
import certifi
import json
from flask_swagger_ui import get_swaggerui_blueprint
import re

app = Flask(__name__)
CORS(app)

# Configure Swagger UI
SWAGGER_URL = '/swagger'
API_URL = 'http://localhost:5000/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sample API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

#construct an error response object
def error_response(code, message):
    print(code)
    print(message)
    return Response(json.dumps({"error": message}), status=code, mimetype="application/json")

# construct a success response object
def success_response(code, content, message = 'Successful operation'):
    response_data = {
        'message': message,
        'data': content
    }
    return Response(json.dumps(response_data), status=code, mimetype="application/json")

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


@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/v1/search/singleCountry', methods=['POST'])
def search_single_country():
    reqBody = request.get_json()
    if ('country' not in reqBody and 'name' not in reqBody):
        return error_response(404, 'Required fields Country and name are missing')
    elif ('country' not in reqBody):
        print('Error: ', reqBody)
        return error_response(404, 'Country field is missing')
    elif ('name' not in reqBody):
        print('Error: ', reqBody)
        return error_response(404, 'name field is missing')
    
    # Get query parameters from the request
    name = reqBody.get('name')
    country = reqBody.get('country')
    state = reqBody.get('state')
    city = reqBody.get('city')
    zipCode = reqBody.get('zipCode')
    address = reqBody.get('address')

    # Initialize a dictionary to group states by country
    query = {}

    # Prepare regex pattern for country, state, and city fields
    def regex_pattern(name):
        return re.compile(r'\b' + re.escape(name.strip()) + r'\b', re.IGNORECASE)

    # Prepare query based on provided parameters
    if country:
        query['country'] = regex_pattern(country)
    if state:
        query['state'] = regex_pattern(state)
    if city:
        query['city'] = regex_pattern(city)
    if zipCode:
        regex = f'^{re.escape(zipCode.strip())}' #not strict match
        query['zipCode'] = {'$regex': regex}
    if name:
        regex = f'^{re.escape(name)}' #not strict match John Smith and Johnathan both allowed
        query['name'] = {'$regex': regex}

    # Prepare regex pattern for partial address search
    if address is not None and address != "":
        query['address'] = {'$regex': f'.*{re.escape(address.strip())}.*', '$options': 'i'}


    # Execute query
    result = list(collection.find(query, {'_id': 0}))

    if not result:
        return success_response(200, result, 'No Addresses Found!')
    
    return success_response(200, result, 'Search successful!')

@app.route('/api/v1/data', methods=['GET'])
def get_data():
    # Query MongoDB to fetch data
    data = collection.find()

    # Initialize a dictionary to group states by country
    country_states = {}

    # Process data from MongoDB
    for document in data:
        country = document.get("country", "")  # Get country, default to empty string if missing
        state = document.get("state", "")  # Get state, default to empty string if missing
        city = document.get("city", "")  # Get city, default to empty string if missing

        if not country or not state or not city:
            continue

        # Initialize dictionaries for country and state if not already present
        if country not in country_states:
            country_states[country] = {}
        if state not in country_states[country]:
            country_states[country][state] = []

        # Add city to the state
        country_states[country][state].append(city)

    return success_response(200, country_states, 'Successfully retrieved country, city and state list')

if __name__ == '__main__':
    app.run(debug=True)
