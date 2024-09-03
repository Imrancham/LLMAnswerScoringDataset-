import re
import os
import csv
import json
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Constants
CSV_HEADERS = ["UserID", "QuestionID", "StudentAnswer", "ResponseRating"]
CSV_FILE_PATH = "/data/ichamieh/LLMAnswerScoringDataset/output/responses.csv"
QUESTION_DIRECTORY = "/data/ichamieh/LLMAnswerScoringDataset/data"
MODEL_SCRIPT_PATH = "/data/ichamieh/LLMAnswerScoringDataset/llama_model.py"
MODEL_CKPT_DIR = "/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct"
TOKENIZER_PATH = "/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct/tokenizer.model"
batch_size = 20
seq_len = 4500

def map_question_key_to_file(key):
    """Map a question key to its corresponding file name."""
    match = re.match(r'^q(\d+)-\d+$', key)
    return f'question{match.group(1)}.txt' if match else None

def load_question_prompt(file_path):
    """Load the question prompt from a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f'File not found: {file_path}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')
    return ""

def generate_prompt(question_prompt, student_answer):
    """Generate the prompt for the LLM by combining question prompt and student answer."""
    return f"{question_prompt} # Antwort des Studierenden: {student_answer}"

def execute_model(dialogs):
    """Execute the LLM model using the provided dialogs."""
    dialogs_json = json.dumps(dialogs)
    command = (
        f"torchrun --nproc_per_node=1 {MODEL_SCRIPT_PATH} "
        f"--student_answer='{dialogs_json}' "
        f"--ckpt_dir={MODEL_CKPT_DIR} "
        f"--tokenizer_path={TOKENIZER_PATH} "
        f"--max_seq_len={seq_len} --max_batch_size={batch_size}"
    )
    return subprocess.run(command, shell=True, text=True, capture_output=True)

def parse_model_output(output):
    """Parse the model output to extract ratings."""
    pattern = r'"content":\s*"(.*?)"'
    return re.findall(pattern, output, re.DOTALL)

def save_responses_to_csv(responses, csv_file_path):
    """Save the responses to the CSV file."""
    file_exists = os.path.isfile(csv_file_path)
    write_header = not file_exists or os.stat(csv_file_path).st_size == 0
    
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if write_header:
            writer.writerow(CSV_HEADERS)
        writer.writerows(responses)

@app.route('/')
def index():
    return 'LLM test'

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    user_id = data['userId']
    dialogs = []
    responses = []


    for key, student_answer in data.items():
        if key == 'userId':
            continue

        file_name = map_question_key_to_file(key)
        if not file_name:
            print("filename:", file_name)
            continue

        file_path = os.path.join(QUESTION_DIRECTORY, file_name)
        question_prompt = load_question_prompt(file_path)
        if not question_prompt:
            continue

        full_prompt = generate_prompt(question_prompt, student_answer)
        dialogs.append(full_prompt)

    #print(dialogs)

    model_result = execute_model(dialogs)

    if model_result.returncode == 0 and model_result.stdout:
        matches = parse_model_output(model_result.stdout)
        filtered_data = ((key, response) for key, response in data.items() if key != "userId")
        for rating, (key, student_answer) in zip(matches, filtered_data):
            responses.append([user_id, key, student_answer, rating])
    else:
        error_message = model_result.stderr if model_result.stderr else "Model execution failed"
        for key, student_answer in filtered_data:
            responses.append([user_id, key, student_answer, error_message])

    save_responses_to_csv(responses, CSV_FILE_PATH)
    
    response_data = {response[1]: response[3] for response in  responses }
 
    return jsonify(response_data)

@app.route('/save', methods=['POST'])
def save_data():
    try:
        form_data = request.json
        user_id = form_data.get('userId')
        
        responses = [
            [user_id, key, value, '']  # Assuming ResponseRating is not provided
            for key, value in form_data.items() if key != 'userId'
        ]

        save_responses_to_csv(responses, 'responses.csv')
        response_data = {key: "Response received" for key in form_data if key != 'userId'}
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
