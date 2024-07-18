import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import csv
import os

app = Flask(__name__)
CORS(app)
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
    for  key, response in data.items():
        if key == 'userId':
            continue  # Skip the userId entry

        # Prepare the prompt and the response
        prompt = """You are a grader for a tenth-grade Science exam in a high school. You will be provided with guidelines, scoring rubric, scoring examples, a question, and a student's response. Tables, if there are any, will be in CSV format. Rate the response according to the scoring rubric and scoring examples. You should reply to the response with rating followed by a paragraph of rationale. For the rating, just report a score only.


# Student Answer: """
        escaped_response = json.dumps(prompt + response)[1:-1]  # json.dumps handles escaping
        print("student answer:", escaped_response)
        command = f'''
        torchrun --nproc_per_node=1 /data/ichamieh/llama3/example_chat_completion.py \\
            --student_answer="{escaped_response}" \\
            --ckpt_dir=/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct/ \\
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

    # Send ratings back to frontend
    return jsonify(ratings)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    