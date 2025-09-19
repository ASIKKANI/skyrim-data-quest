# chatbot_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# Replace with your actual Gemini API key
API_KEY = "AIzaSyCIyPFCvSMqvgd2-zHgfHJT7VWw-AsBGyU"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

# Directory containing saved email JSONs
SAVED_EMAILS_DIR = "saved_emails"

def get_gemini_response(user_prompt, email_context=None):
    """
    Sends user prompt (with optional email context) to Gemini API.
    """
    headers = {"Content-Type": "application/json"}

    full_prompt = ""
    if email_context:
        full_prompt += f"Email content:\n{email_context}\n\n"
    full_prompt += f"User question: {user_prompt}"

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "systemInstruction": {
            "parts": [{"text": "You are a helpful assistant named 'Gemini'. Answer clearly and concisely."}]
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        bot_response = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Sorry, I could not generate a response.')
        return bot_response
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    email_file = data.get('email_file')  # optional

    email_context = None
    if email_file:
        email_path = os.path.join(SAVED_EMAILS_DIR, email_file)
        if os.path.exists(email_path):
            try:
                with open(email_path, 'r', encoding='utf-8') as f:
                    email_data = json.load(f)
                # Use email body or fallback to full JSON string
                email_context = email_data.get('body', json.dumps(email_data))
            except Exception as e:
                email_context = f"Failed to read email file: {e}"

    if not prompt:
        return jsonify({"response": "Please provide a question."})

    bot_response = get_gemini_response(prompt, email_context=email_context)
    return jsonify({"response": bot_response})

@app.route('/list_emails', methods=['GET'])
def list_emails():
    """
    Returns a list of email JSON filenames in saved_emails directory
    """
    try:
        files = [f for f in os.listdir(SAVED_EMAILS_DIR) if f.endswith('.json')]
        return jsonify(files)
    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    print("Starting chatbot server on http://127.0.0.1:5000")
    app.run(debug=True)
