# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed in accordance with the terms of the Llama 3 Community License Agreement.

import json
from typing import List, Optional

import fire

from llama import Dialog, Llama


def main(
    ckpt_dir: str,
    tokenizer_path: str,
    student_answer: str,
    temperature: float = 0,
    top_p: float = 0.9,
    max_seq_len: int = 2056,
    max_batch_size: int = 4,
    max_gen_len: Optional[int] = None,
):
    """
    Examples to run with the models finetuned for chat. Prompts correspond of chat
    turns between the user and assistant with the final one always being the user.

    An optional system prompt at the beginning to control how the model should respond
    is also supported.

    The context window of llama3 models is 8192 tokens, so `max_seq_len` needs to be <= 8192.

    `max_gen_len` is optional because finetuned models are able to stop generations naturally.
    """
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    # Parse the JSON string into a Python list
# Check if student_answer is a string (JSON) or a list
    if isinstance(student_answer, str):
        try:
            st_answers = json.loads(student_answer)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            st_answers = []  # Handle empty or invalid JSON
    elif isinstance(student_answer, list):
        st_answers = student_answer
    else:
        print(f"Unexpected type for student_answer: {type(student_answer)}")
        st_answers = []
    dialogs: List[Dialog] = [     [{"role": "user", "content": answer}] for answer in st_answers
                             ]
    


    results = generator.chat_completion(
        dialogs,
        max_gen_len=max_gen_len,
        temperature=temperature,
        top_p=top_p,
    )

    # Modified output: print only the final generation's role and content
      # Modified output: print only the final generation's role and content
    
    # Assuming 'results' is a list of dictionaries with 'generation' containing 'role' and 'content'
    results_dicts = [{'role': answer['generation']['role'], 'content': answer['generation']['content']} for answer in results]

    # Convert the list of dictionaries to a JSON-formatted string
    json_string = json.dumps(results_dicts, indent=4)

    # Print or use the JSON string as needed
    print(json_string)
if __name__ == "__main__":
    fire.Fire(main)
