from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Load the DistilBERT model for question-answering
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/ask-question', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question')
        context = data.get('context')

        # Get the answer from the model
        result = qa_pipeline(question=question, context=context)
        answer = result['answer']

        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
