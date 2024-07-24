import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import csv
import os
import re

app = Flask(__name__)
CORS(app)

def map_question_key(key):
    # Use a regular expression to parse the key
    match = re.match(r'^q(\d+)-\d+$', key)
    if match:
        # If the pattern matches, return the formatted question string
        return f'question{match.group(1)}.txt'
    else:
        # Return None or an appropriate error message if the key format is incorrect
        return None


@app.route('/')
def index():
    return 'LLM test'
@app.route('/submit', methods=['POST'])
def submit():
    # Receive data as JSON
    data = request.json
    userId = data['userId']  # Assuming a 'userId' is always included

    # Assume each key in data corresponds to a question response
    ratings = {}
    responses = []

    for  key, response in data.items():
        if key == 'userId':
            continue  # Skip the userId entry

        # Prepare the prompt and the response
        prompt = """You are a grader for a tenth-grade Science exam in a high school. You will be provided with guidelines, scoring rubric, scoring examples, a question, and a student's response. Tables, if there are any, will be in CSV format. Rate the response according to the scoring rubric and scoring examples. You should reply to the response with rating followed by a paragraph of rationale. For the rating, just report a score only.

# Student Answer: """
        fileName = map_question_key(key)
        directory= "./data"


        file_path = os.path.join(directory, fileName)
        try:
            # Attempt to open and read the file
            with open(file_path, 'r') as file:
                prompt =  file.read()
        except FileNotFoundError:
            # If the file does not exist, return an error message
            print( f'File not found: {file_path}')
        except Exception as e:
            # Handle other possible exceptions
            print( f'An error occurred: {str(e)}')



        escaped_response = json.dumps(prompt +" # Antwort der Studenten: "+ response)[1:-1]  # json.dumps handles escaping
        print( escaped_response)
        command = f'''
        torchrun --nproc_per_node=1 /data/ichamieh/LLMAnswerScoringDataset/llama_server.py \\
            --student_answer="{escaped_response}" \\
            --ckpt_dir=/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct \\
            --tokenizer_path=/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct/tokenizer.model \\
            --max_seq_len=2500 --max_batch_size=6
            
        '''

        # Run the command
        result = subprocess.run(command, shell=True, text=True, capture_output=True)

        # Process the result
        if result.returncode == 0:
            # Use regex to extract the desired output
            match = re.search(r'Assistant:\s*(.*)', result.stdout, re.DOTALL)
            if match:
                ratings[key] = match.group(1).strip()
            else:
                ratings[key] = "No valid response found."
        else:
            ratings[key] = f"Error: {result.stderr}"

        # Save the student id, question id, student answer, and response to a list
        responses.append([userId, key, response, ratings[key]])

    # Save to CSV
    csv_file_path = "/data/ichamieh/LLMAnswerScoringDataset/output/responses.csv"
    file_exists = os.path.isfile(csv_file_path)
    write_header = not file_exists or os.stat(csv_file_path).st_size == 0

    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if write_header:
            writer.writerow(["UserID", "QuestionID", "StudentAnswer", "ResponseRating"])  # Write header only once
        writer.writerows(responses)

    # Send ratings back to frontend
    return jsonify(ratings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    