from flask import Flask, request, jsonify, send_from_directory
from pydanticModels import process_models
from apiCreator import create_api
import os
from main import get_database_info, host, user, password, database_name, main

app = Flask(__name__)

@app.route('/sql_code', methods=['POST'])
def sql_code():
    data = request.json
    if data is None:
        return jsonify({"error": "No JSON data provided"}), 400

    # Creating API
    try:
        create_api(data)
    except:
        print("Error while creating API happened")
    api = ""
    # Get the directory of the current file
    current_directory = os.path.dirname(__file__)
    # Join the directory path with the filename
    api_file_path = os.path.join(current_directory, 'crud_api.py')
    print(api_file_path)
    with open(api_file_path) as file:
        # Read the entire content of the file crud_api.py
        api = file.read()
    
    # Database info
    print("OCHKO 1")
    main(host, user, password, database_name, data)
    print("OCHKO 2")
    db_info = get_database_info(host, user, password, database_name)
    print(db_info)

    # Return a JSON response
    return jsonify({"sql_code": data, "api": api, "db_info": db_info}), 200

@app.route('/', methods=['GET'])
def default_endpoint():
    return send_from_directory("frontend", "index.html")

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend', filename)

def start_server():
    app.run(debug=True)