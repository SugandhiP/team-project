from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import pymongo
from pymongo import MongoClient 
from bson.json_util import dumps
from collections import defaultdict
import certifi
import json
from flask_swagger_ui import get_swaggerui_blueprint
import re

app = Flask(__name__)
CORS(app)

# testData = {
#     "name": "Luz Burns",
#     "country": "India",
#     #"countries": null,
#     "state": "Maharashtra",
#     "city": "Vasai-Virar",
#     "zipCode": "522530",
#     "address": "Brahmanapalle - Regulagadda Road"
# }

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

def prepare_query(reqBody, query):
    # Get query parameters from the request
    name = reqBody.get('name')
    country = reqBody.get('country')
    state = reqBody.get('state')
    city = reqBody.get('city')
    zipCode = reqBody.get('zipCode')
    address = reqBody.get('address')
    # Prepare query based on provided parameters
    if country is not None and country != "":
        query['country'] = {'$regex': country.strip(), '$options': 'i'} 
    if state is not None and state != "":
        query['state'] = {'$regex': re.escape(state.strip()), '$options': 'i'}
    if city is not None and city != "":
        query['city'] = {'$regex': re.escape(city.strip()), '$options': 'i'} 
    if zipCode is not None and zipCode != "":
        query['zipCode'] = {'$regex': f'.*{re.escape(zipCode.strip())}.*', '$options': 'i'}
    if name:
        # regex = f'^{re.escape(name)}' #not strict match John Smith and Johnathan both allowed
        # query['name'] = {'$regex': regex, '$options':'i'}
        query['name'] = {'$regex': f'.*{re.escape(name.strip())}.*', '$options': 'i'}

    #Prepare regex pattern for partial address search
    if address is not None and address != "":
        query['address'] = {'$regex': f'.*{re.escape(address.strip())}.*', '$options': 'i'}
    return query

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

#optimize query
# collection.create_index([("country", pymongo.ASCENDING)])
# collection.create_index([("name", pymongo.ASCENDING)])

@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/v1/search/singleCountry', methods=['POST'])
def search_single_country():
    reqBody = request.get_json()
    error_messages = []

    if 'country' not in reqBody or not reqBody['country']:
        error_messages.append('Country field is missing or empty')
    if 'name' not in reqBody or not reqBody['name']:
        error_messages.append('Name field is missing or empty')
    
    if error_messages:
        error_message = ', '.join(error_messages)
        return error_response(400, error_message)
    
    # Get query parameters from the request
    name = reqBody.get('name')
    country = reqBody.get('country')
    state = reqBody.get('state')
    city = reqBody.get('city')
    zipCode = reqBody.get('zipCode')
    address = reqBody.get('address')

    # Initialize a dictionary to group states by country
    query = {}

    # Prepare query based on provided parameters
    if country:
        query['country'] = {'$regex': country.strip(), '$options': 'i'} 
    if state:
        query['state'] = {'$regex': re.escape(state.strip()), '$options': 'i'}
    if city:
        query['city'] = {'$regex': re.escape(city.strip()), '$options': 'i'} 
    if zipCode is not None and zipCode != "":
        # regex = f'^{re.escape(zipCode.strip())}' #not strict match
        # query['zipCode'] = {'$regex': regex}
        query['zipCode'] = {'$regex': f'.*{re.escape(zipCode.strip())}.*', '$options': 'i'}
    if name:
        regex = f'^{re.escape(name)}' #not strict match John Smith and Johnathan both allowed
        query['name'] = {'$regex': regex, '$options': 'i'}

    # Prepare regex pattern for partial address search
    if address is not None and address != "":
        query['address'] = {'$regex': f'.*{re.escape(address.strip())}.*', '$options': 'i'}

    # Execute query
    print(query)
    result = list(collection.find(query, {'_id': 0}).limit(200))

    if not result:
        return success_response(200, result, 'No Addresses Found!')
    
    return success_response(200, result, 'Search successful!')


@app.route('/api/v1/search/multiCountry', methods=['POST'])
def search_multi_country():
    reqBody = request.get_json()
    error_messages = []

    if 'name' not in reqBody or not reqBody['name']:
        error_messages.append('Name field is missing or empty')

    if error_messages:
        error_message = ', '.join(error_messages)
        return error_response(400, error_message)
    
    print("This is name", reqBody['name'])
    
    # query['country'] = "USA"
    # # Get query parameters from the request
    name = reqBody.get('name')
    countries = []
    countries = reqBody.get('countries')
    state = reqBody.get('state')
    city = reqBody.get('city')
    zipCode = reqBody.get('zipCode')
    address = reqBody.get('address')

    # Initialize a dictionary to group states by country
    query = {}
    search_result = []

    if not reqBody['countries']:
        countries = {"USA","UK","Canada","India","Spain","Germany","Sweden","Japan","Brazil","Mexico","South Korea"} 

    for country in countries:
        query = {'country': country}
    
        # Prepare query based on provided parameters
        if country is not None and country != "":
            query['country'] = {'$regex': country.strip(), '$options': 'i'} 
        if state is not None and state != "":
            query['state'] = {'$regex': re.escape(state.strip()), '$options': 'i'}
        if city is not None and city != "":
            query['city'] = {'$regex': re.escape(city.strip()), '$options': 'i'} 
        if zipCode is not None and zipCode != "":
            query['zipCode'] = {'$regex': f'.*{re.escape(zipCode.strip())}.*', '$options': 'i'}
        if name:
            # regex = f'^{re.escape(name)}' #not strict match John Smith and Johnathan both allowed
            # query['name'] = {'$regex': regex, '$options':'i'}
            query['name'] = {'$regex': f'.*{re.escape(name.strip())}.*', '$options': 'i'}

        #Prepare regex pattern for partial address search
        if address is not None and address != "":
            query['address'] = {'$regex': f'.*{re.escape(address.strip())}.*', '$options': 'i'}
    
        #query = prepare_query(reqBody, query)

        # # Count the number of matching documents
        # result_count = result_count + collection.count_documents(query)    

        # print("count ",result_count)

        # Limit the number of documents returned if it exceeds 200
        # if result_count > 200:
        #     print("Inside loop ",result_count)
        #     result = list(collection.find(query, {'_id': 0}))
        #     search_result.extend(result)
        #     return success_response(200, result, 'Search successful!')
        # else:
        #     result = list(collection.find(query, {'_id': 0}))
        print(query)
        result = list(collection.find(query, {'_id': 0}))
        #print(result)
        search_result.extend(result)    

    if not search_result:
        return success_response(200, [], 'No Addresses Found!')
    
    return success_response(200, search_result[:200], 'Search successful!')

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
