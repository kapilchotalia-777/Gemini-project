from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import io

app = Flask(__name__)

# API Key for Google Generative AI (Gemini)
API_KEY = "AIzaSyBOYQtwMZbF3rTMBt2y_kPjgvn36TTfJpc"
genai.configure(api_key=API_KEY)

# Global variable to store the extracted text
extracted_text = ""
text_sections = []

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file):
    text = file.read().decode('utf-8')
    return text

def segment_text(text):
    # Split text into sections based on paragraph breaks or other delimiters
    return text.split('\n\n')  # Assuming paragraphs are separated by double new lines

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global extracted_text, text_sections
    extracted_text = ""
    text_sections = []
    
    if 'files' not in request.files:
        return "No file part", 400
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return "No selected file", 400

    for file in files:
        if file.filename.endswith('.pdf'):
            extracted_text += extract_text_from_pdf(file)
        elif file.filename.endswith('.docx'):
            extracted_text += extract_text_from_docx(file)
        elif file.filename.endswith('.txt'):
            extracted_text += extract_text_from_txt(file)
        else:
            return "Unsupported file type", 400

    text_sections = segment_text(extracted_text)
    return "Files uploaded and text extracted", 200

@app.route('/ask', methods=['POST'])
def ask_question():
    global text_sections
    data = request.json
    question = data.get('question')

    if not text_sections:
        return jsonify({'answer': 'No text available. Please upload a file first.'}), 400

    # Find the most relevant section based on the question
    relevant_section = find_relevant_section(question, text_sections)

    if not relevant_section:
        return jsonify({'answer': 'No relevant section found in the text.'}), 404

    # Generate initial answer from the relevant section
    initial_answer = generate_initial_answer(question, relevant_section)

    # Enhance the answer using Google Generative AI (Gemini)
    final_answer = enhance_answer(question, initial_answer)

    return jsonify({'answer': final_answer}), 200

def find_relevant_section(question, sections):
    # Simple keyword matching to find the most relevant section
    for section in sections:
        if any(keyword in section.lower() for keyword in question.lower().split()):
            return section
    return None

def generate_initial_answer(question, section):
    # This function generates a basic answer based on the relevant section
    # You can use a simple approach like extracting relevant sentences or paragraphs
    prompt = (
        f"Based on the following context, answer the question in no more than 150 words. "
        f"Context: {section}\n"
        f"Question: {question}"
    )
    return prompt

def enhance_answer(question, initial_answer):
    # Enhance the initial answer using Google Generative AI (Gemini)
    prompt = (
        f"Improve the following answer based on the given question. Provide a detailed and clear response. "
        f"Question: {question}\n"
        f"Initial Answer: {initial_answer}"
    )
    try:
        response = genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during API request: {e}")
        return 'An error occurred while enhancing the answer.'

# if __name__ == '__main__':
#     app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
