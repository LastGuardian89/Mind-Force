import datetime
import os

def get_input_data():
    return input("Enter your question/code/link or upload: ")

def send_response_to_user(response):
    print("\n\n[Final Response]:\n", response)

def log_request(prompt, response):
    log_line = f"{datetime.datetime.now().isoformat()} | PROMPT: {prompt}\nRESPONSE: {response}\n{'='*80}\n"
    with open("logs/request_log.txt", "a") as log_file:
        log_file.write(log_line)