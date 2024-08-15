import ast
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import csv
import os

app = Flask(__name__)
CORS(app)

def map_question_key(key):
    match = re.match(r'^q(\d+)-\d+$', key)
    if match:
        return f'question{match.group(1)}.txt'
    else:
        return None

@app.route('/')
def index():
    return 'LLM test'

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    userId = data['userId']
    responses = []
    prompt = """You are a grader for a tenth-grade Science exam in a high school. You will be provided with guidelines, scoring rubric, scoring examples, a question, and a student's response. Tables, if there are any, will be in CSV format. Rate the response according to the scoring rubric and scoring examples. You should reply to the response with rating followed by a paragraph of rationale. For the rating, just report a score only.

# Student Answer: """
    dialogs = []
    for key, response in data.items():
        if key == 'userId':
            continue

        fileName = map_question_key(key)
        directory= "/data/ichamieh/LLMAnswerScoringDataset/data"


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
        
        escaped_response = prompt + " # Antwort der Studenten: " + response
        dialogs.append( escaped_response)

    dialogs_json = json.dumps(dialogs)



    command = f'''
    torchrun --nproc_per_node=1 /data/ichamieh/LLMAnswerScoringDataset/llama_model.py \\
        --student_answer='{dialogs_json}' \\
        --ckpt_dir=/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct \\
        --tokenizer_path=/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct/tokenizer.model \\
        --max_seq_len=4500 --max_batch_size=20
    '''

    result = subprocess.run(command, shell=True, text=True, capture_output=True)



    ratings = {}
    if result.returncode == 0:

        if result.stdout:            
            # Regex pattern to find all content values
            pattern = r'"content":\s*"(.*?)"'
            # Finding all matches in the JSON string
            matches = re.findall(pattern, result.stdout, re.DOTALL)

            # Creating a generator that skips certain keys in the data
            filtered_data = ((key, response) for key, response in data.items() if key != "userId")

            for match, (key, response) in zip(matches, filtered_data):
                print(match)

                ratings[key] = match
                responses.append([userId, key, response, match])

        else:
            ratings[key] = f"Error: {result.stderr}"
            responses.append([userId, key, response, f"Error: {result.stderr}"])
            

    csv_file_path = "/data/ichamieh/LLMAnswerScoringDataset/output/responses.csv"
    file_exists = os.path.isfile(csv_file_path)
    write_header = not file_exists or os.stat(csv_file_path).st_size == 0

    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        if write_header:
            writer.writerow(["UserID", "QuestionID", "StudentAnswer", "ResponseRating"])
        writer.writerows(responses)

    return jsonify(ratings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
