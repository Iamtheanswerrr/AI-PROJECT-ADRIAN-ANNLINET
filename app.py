from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import json
import os
import spacy

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load FAQ data
faq_file = 'faqs.json'
if not os.path.exists(faq_file):
    raise FileNotFoundError(f"'{faq_file}' file not found. Please ensure it exists in the project directory.")

try:
    with open(faq_file, 'r') as f:
        faqs = json.load(f)
except json.JSONDecodeError:
    raise ValueError(f"The '{faq_file}' file contains invalid JSON.")

# Prepare data
questions = [faq.get('question', '') for faq in faqs]
answers = [faq.get('answer', '') for faq in faqs]
tags_dict = {faq.get('question', ''): faq.get('tags', []) for faq in faqs}

# Prepare word-based direct responses if applicable
word_answers = {}
for faq in faqs:
    tags = faq.get('tags', [])
    for tag in tags:
        word_answers[tag.lower()] = faq.get('answer', '')

# Load SentenceTransformer model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embeddings = model.encode(questions, convert_to_tensor=True)
except Exception as e:
    raise RuntimeError(f"Failed to load SentenceTransformer model: {str(e)}")

# Load spaCy model for entity recognition (optional, but useful for extracting entities like dates, locations)
nlp = spacy.load('en_core_web_sm')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('question', '').strip().lower()

        if not query:
            return jsonify({"error": "No question provided."}), 400

        # Optional: Entity recognition with spaCy
        doc = nlp(query)
        entities = [ent.text for ent in doc.ents]

        # Check if the query matches a single word (tag)
        if query in word_answers:
            return jsonify({
                "answer": word_answers[query],
                "tags": list(word_answers.keys())  # Optional tags menu
            })

        # Use semantic similarity for free-text queries
        query_embedding = model.encode(query, convert_to_tensor=True)
        similarity_scores = util.pytorch_cos_sim(query_embedding, question_embeddings)
        best_match_idx = similarity_scores.argmax().item()
        best_match_score = similarity_scores[0][best_match_idx].item()

        # Threshold for similarity matching
        threshold = 0.7  # Adjust this based on testing
        if best_match_score >= threshold:
            matched_question = questions[best_match_idx]
            response_tags = tags_dict.get(matched_question, [])
            return jsonify({
                "answer": answers[best_match_idx],
                "tags": response_tags,
                "entities": entities  # Return extracted entities (optional)
            })

        # If no match is found or similarity score is too low
        return jsonify({
            "answer": "Sorry, I couldn't find an exact answer to your question. :( "
                      "  Would you like to contact us for more assistance? Email: support@davlibrary.com | Hotline: 017-024-789",
            "tags": list(word_answers.keys()),  # Optional tags menu
            "entities": entities  # Return extracted entities (optional)
        })

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/tags', methods=['GET'])
def get_tags():
    # API endpoint to fetch all available tags
    return jsonify({
        "tags": list(word_answers.keys())
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
