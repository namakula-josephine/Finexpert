import os
import sqlite3
import pickle
import openai
from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load vectorizer
vectorizer_filename = 'vectorizer.pkl'
vectorizer = joblib.load(vectorizer_filename)

# Set your OpenAI API key
openai.api_key = 'secret key here'  # Replace with your actual API key

# Database details
db_name = 'financial_decision_making corpus.db'
table_name = 'documents'

def vectorize_query(query, vectorizer):
    query_vector = vectorizer.transform([query])
    return query_vector

def retrieve_documents(query, vectorizer, db_name, table_name, top_n=3):
    query_vector = vectorize_query(query, vectorizer)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, text, vector FROM {table_name}")
    rows = cursor.fetchall()

    doc_scores = []
    for row in rows:
        doc_id, text, vector_blob = row
        doc_vector = pickle.loads(vector_blob)
        similarity = cosine_similarity(query_vector, doc_vector)
        doc_scores.append((similarity, text))

    doc_scores.sort(reverse=True, key=lambda x: x[0])
    top_documents = [doc[1] for doc in doc_scores[:top_n]]

    conn.close()

    return top_documents

@app.route('/query', methods=['POST'])
def query():
    print("Received a query request")
    data = request.get_json()
    print("Request data:", data)
    query = data.get('query', None)  # Fixing this line
    if query is None:
        return jsonify({'error': 'No query provided'}), 400

    top_documents = retrieve_documents(query, vectorizer, db_name, table_name)
    
    prompt = f"Q: {query}\n"
    for i, doc in enumerate(top_documents, 1):
        prompt += f"Context {i}: {doc}\n"
    prompt += "A:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.7
    )

    answer = response['choices'][0]['message']['content'].strip()
    return jsonify({'query': query, 'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
