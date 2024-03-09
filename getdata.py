from flask import Flask, jsonify, request, Response
from pymongo import MongoClient 
from bson.json_util import dumps
from collections import defaultdict
import certifi
import json
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

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
    if ('country' not in reqBody):
        print('Error: ', reqBody)
        return error_response(404, 'Country field is missing')
    query = {}
    for (key, val) in reqBody.items():
        if (key in ['city', 'state', 'address', 'zipCode', 'name']):
            query[key] = {"$regex": ".*" + val + ".*"}
        elif (key == 'country'):
            query[key] = val
            # query[k] = {"$in": v}
    # Get data from DB
    result = []
    return success_response(200, result, 'Search successful!')

@app.route('/api/v1/data', methods=['GET'])
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

        # Initialize dictionaries for country and state if not already present
        if country not in country_states:
            country_states[country] = {}
        if state not in country_states[country]:
            country_states[country][state] = []

        # Add city to the state
        country_states[country][state].append(city)

    # Convert the country_states dictionary to a list
    #for data in country_states.items():
        #json_data.append(data)

    return success_response(200, country_states, 'Successfully retrieved country, city and state list')

if __name__ == '__main__':
    app.run(debug=True)
