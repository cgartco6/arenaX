import requests
import os
import argparse
import time
from dotenv import load_dotenv

load_dotenv()

HF_API = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neox-20b"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

def generate_code(prompt, max_retries=3):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    
    for attempt in range(max_retries):
        response = requests.post(HF_API, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        elif response.status_code == 503:  # Model loading
            time.sleep(30)
        else:
            raise Exception(f"API Error: {response.text}")
    
    raise Exception("Max retries exceeded")

def self_improve(file_path):
    with open(file_path, 'r') as f:
        code = f.read()
    
    prompt = f"""Improve this code for performance, security, and maintainability:
    
{code}

Improved version:
"""
    
    improved_code = generate_code(prompt)
    
    # Save backup before overwriting
    with open(f"{file_path}.bak", 'w') as f:
        f.write(code)
    
    with open(file_path, 'w') as f:
        f.write(improved_code)
    
    return improved_code

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File to improve")
    args = parser.parse_args()
    
    if args.file:
        print("Improving code...")
        result = self_improve(args.file)
        print(f"Code improvement complete. Backup saved to {args.file}.bak")
    else:
        print("Please specify a file with --file")
