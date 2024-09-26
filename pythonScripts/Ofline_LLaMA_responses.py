import csv
import os
import json
import re
import subprocess
import argparse
import html



# Constants (update these paths based on your environment)
MODEL_SCRIPT_PATH = '/data/ichamieh/LLMAnswerScoringDataset/llama_model.py'
MODEL_CKPT_DIR = '/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct'
TOKENIZER_PATH = '/data/ichamieh/llama3/Meta-Llama-3-8B-Instruct/tokenizer.model'
seq_len = 2024  # adjust as necessary
batch_size = 8  # adjust as necessary
QUESTION_DIRECTORY = '/data/ichamieh/LLMAnswerScoringDataset/data'
CSV_HEADERS = ["UserID", "QuestionID", "StudentAnswer", "ResponseRating"]

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

def decode_and_replace(text):
            if not isinstance(text, str):
                return text  # If not a string, return as is

            # Decode Unicode escape sequences and replace newlines with <br> tags
            text = text.encode('utf-8').decode('unicode_escape')  # Decode Unicode escapes
            text = html.unescape(text)  # Replace HTML entities
            return text.replace('\n', ' ')  # Replace newlines with <br>

def parse_model_output(output):
    """
    Parses the model output to extract the content, replacing Unicode escapes and HTML entities.
    """
    try:
        # Function to replace Unicode escapes and newlines
        

        # Regex to extract content from the model output
        pattern = r'"content":\s*"(.*?)"'
        matches = re.findall(pattern, output, re.DOTALL)

        # Process each match (content) to decode and replace escapes
        return [decode_and_replace(match) for match in matches]
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return matches

def map_question_key_to_file(key):
    """Map a question key to its corresponding file name."""
    if key[2]== '-':
        match = key[1:2]
    else:
        match = key[1]
    #match = re.match(r'^q(\d+)-\d+$'+'-', key)
    return f'question-{match}.txt' if match else None

def save_responses_to_csv(responses, csv_file_path):
    """Save the responses to the CSV file."""
    file_exists = os.path.isfile(csv_file_path)
    write_header = not file_exists or os.stat(csv_file_path).st_size == 0
    
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        if write_header:
            writer.writerow(CSV_HEADERS)
        writer.writerows(responses)

def update_csv_with_model_responses(csv_file_path):
    """Read the CSV, generate prompts, get responses, and update the CSV file."""
    try:
        with open(csv_file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        
        for row in rows:
            updated_responses = []
            dialogs = []
            user_id = row['UserId']
            question_id = row['QuestionID']
            student_answer = row['StudentAnswer']

            # Get question prompt
            file_name = map_question_key_to_file(question_id)
            if not file_name:
                print(f"Question file not found for QuestionID: {question_id}")
                continue

            file_path = os.path.join(QUESTION_DIRECTORY, file_name)
            question_prompt = load_question_prompt(file_path)
            if not question_prompt:
                print(f"Could not load prompt for QuestionID: {question_id}")
                continue

            full_prompt = generate_prompt(question_prompt, student_answer)
            dialogs.append(full_prompt)

            # Execute the model
            model_result = execute_model(dialogs)

            if model_result.returncode == 0 and model_result.stdout:
                matches = parse_model_output(model_result.stdout)
                row['ResponseRating'] = matches
                updated_responses.append([row['UserId'],  row['QuestionID'], row['StudentAnswer'] , row['ResponseRating']])
                save_responses_to_csv(updated_responses, 'res.csv')

            else:
                print("Model execution failed.")
                error_message = model_result.stderr if model_result.stderr else "Model execution failed"
                row['ResponseRating'] = error_message
                updated_responses.append([row['UserId'],  row['QuestionID'], row['StudentAnswer'] , row['ResponseRating']])
                save_responses_to_csv(updated_responses, 'res.csv')          

            # Write the updated rows back to the CSV file

            print(f"CSV file '{csv_file_path}' updated successfully.")
    except Exception as e:
        print(f"An error occurred while updating the CSV: {str(e)}")



if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Update a CSV file with model responses.")
    parser.add_argument("csv_file_path", help="Path to the CSV file to be updated")
    args = parser.parse_args()

    # Run the CSV update function with the provided CSV file path
    update_csv_with_model_responses(args.csv_file_path)
