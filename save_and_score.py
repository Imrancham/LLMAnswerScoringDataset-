from flask import Flask, request, jsonify
from flask_cors import CORS

import csv
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and origins


@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    print("get a request")

    file_exists = os.path.isfile('responses.csv')
    with open('responses.csv', 'a', newline='') as csvfile:
        fieldnames = [
            'q1-1', 'q1-2', 'q1-3', 'q1-4', 'q1-5',
            'q2-1', 'q2-2', 'q2-3', 'q2-4', 'q2-5',
            'q3-1', 'q3-2', 'q3-3', 'q3-4', 'q3-5',
            'q4-1', 'q4-2', 'q4-3', 'q4-4', 'q4-5',
            'q5-1', 'q5-2', 'q5-3', 'q5-4', 'q5-5',
            'q6-1', 'q6-2', 'q6-3', 'q6-4', 'q6-5',
            'q7-1', 'q7-2', 'q7-3', 'q7-4', 'q7-5',
            'q8-1', 'q8-2', 'q8-3', 'q8-4', 'q8-5',
            'q9-1', 'q9-2', 'q9-3', 'q9-4', 'q9-5',
            'q10-1', 'q10-2', 'q10-3', 'q10-4', 'q10-5',
            'consent' 
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    
    return jsonify({"message": "Data received and saved"}), 200

if __name__ == '__main__':
    #basic_url='0.0.0.0'
    #app.run(host=basic_url, port=8080)
    #cors = CORS(app, resources={r"/*": {"origins": "*"}})  # Allow requests from any origin

    app.run(debug=True)
