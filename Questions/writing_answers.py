import json
import signal
import sys

# Function to load the questions from a JSON file
def load_questions(filepath):
    try:
        with open(filepath, 'r') as file:
            data_dict = json.load(file)
        return data_dict
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        sys.exit(1)

# Function to read the last key from a file
def read_last_key(filepath):
    try:
        with open(filepath, 'r') as file:
            last_key = file.read().strip()  # Ensure whitespace is stripped
        return last_key
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return None

# Function to write the last key to a file
def write_last_key(filepath, last):
    with open(filepath, 'w') as file:
        file.write(str(last))

# Function to save progress to a JSON file
def save_progress(filepath, data):
    with open(filepath, 'w') as file:  # Note the change to 'w' to overwrite and ensure valid JSON
        json.dump(data, file, indent=4)
    print("Progress saved.")

# Signal handler for graceful exit
def signal_handler(sig, frame):
    print('Exiting and saving progress...')
    save_progress('Questions/QAC.json', answer_dict)
    sys.exit(0)

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Main program
if __name__ == "__main__":
    data_dict = load_questions('Questions/QA.json')
    last_key = read_last_key("Questions/last.txt")
    last = int(last_key) if last_key and last_key.isdigit() else 0

    answer_dict = {}
    for key, value in data_dict.items():
        if int(key) <= last:
            continue
        print(key, '\n', [f'{answer}\n' for answer in value['answers']])
        answer = input('\nAnswer (type "exit" to save and quit): ')
        if answer.lower() == "exit":
            break
        while answer == "" or len(answer) >1:
            answer = input('\nAnswer:  ')
        answer_dict[key] = value
        answer_dict[key]['correct'] = answer
        last = int(key)  # Update last to the current key after processing
        write_last_key("Questions/last.txt", last)

    save_progress('Questions/QAC.json', answer_dict)
    print("Finished processing questions.")
