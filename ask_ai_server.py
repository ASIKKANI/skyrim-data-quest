from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

API_KEY = "AIzaSyCIyPFCvSMqvgd2-zHgfHJT7VWw-AsBGyU"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

app = Flask(__name__)
CORS(app)

def get_gemini_response(user_prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "systemInstruction": {
            "parts": [{"text": "You are a friendly, helpful, and concise assistant. Your name is 'Gemini'."}]
        }
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        bot_response_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Sorry, I could not generate a response.')
        return bot_response_text
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.get_json()
    question = data.get('question', '')
    email_subject = data.get('emailSubject', '')
    email_body = data.get('emailBody', '')
    # Compose a prompt that includes the email context
    user_prompt = f"Email Subject: {email_subject}\nEmail Body: {email_body}\n\nUser Question: {question}\n\nAnswer concisely:"
    answer = get_gemini_response(user_prompt)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(port=3000, debug=True)