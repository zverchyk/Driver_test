import PyPDF2
import re
import json
# # Open the PDF file in binary read mode
# with open('Questions\Alberta-Basic-Licence-Drivers-Assessment-6 (1).pdf', 'rb') as file:
#     # Create a PDF reader object
#     reader = PyPDF2.PdfReader(file)
    
#     # If you want to read all pages of the PDF
     
#     # Open a new text file in write mode
#     with open('Questions/questions.txt', 'w', encoding='utf-8') as text_file:
#         # Read all pages of the PDF
#         for page in reader.pages:
#             # Extract text from the current page
#             text = page.extract_text()
#             # Write the extracted text to the text file, add a newline between pages
#             if text:  # Check if text extraction was successful
#                 text_file.write(text + "\n")
#             else:
#                 text_file.write("Could not extract text from this page.\n")

        
    
#     # Or if you just want to read the first page
#     # first_page = reader.pages[0]
#     # print(first_page.extract_text())
with open('Questions/questions.txt', 'r') as file:
    text = file.read()
# Split the text into lines
# Split the text into individual questions
questions = re.split(r"\n(?=\d+\.)", text.strip())

def parse_question(question_block):
    parts = re.split(r"\n(?=[abcd]\.)", question_block)
    question_text = parts[0]
    answers = parts[1:]
    
    question_match = re.match(r"(\d+)\. (.+)", question_text)
    if question_match:
        question_number, question = question_match.groups()
    else:
        return None  # or handle the error as appropriate
    
    answers = [re.match(r"[abcd]\. (.+)", answer).group(1) for answer in answers if re.match(r"[abcd]\. (.+)", answer)]
    
    return {
        "question": question,
        "answers": answers
    }

# Filter out any None values returned by parse_question
questions_dict = {int(re.match(r"(\d+)", q).group(0)): parse_question(q) for q in questions if parse_question(q)}
# ensure_ascii keeps all characters like they are
json_data = json.dumps(questions_dict, ensure_ascii=False)
with open('AQ.json', 'w') as file:
    file.write(json_data)

