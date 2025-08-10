import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO in production
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.route('/')
def home():
    return "Welcome to Server!"

@app.route("/llm/query", methods=["POST"])
def llm_query():
    logging.debug("📩 Received request at /llm/query")

    data = request.get_json()
    logging.debug(f"📝 Request data: {data}")

    user_text = data.get("text", "").strip()
    if not user_text:
        logging.error("❌ No text provided by client")
        return jsonify({"error": "Text input is required"}), 400

    url = f"https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "prompt": {"text": user_text},
        "temperature": 0.7,
        "maxOutputTokens": 256,
    }

    logging.debug("🌐 Sending request to Gemini API")
    try:
        response = requests.post(url, headers=headers, json=payload)
        logging.debug(f"🔍 Raw Gemini API response: {response.text}")

        if response.status_code != 200:
            logging.error(f"❌ Gemini API request failed with status {response.status_code}")
            return jsonify({"error": "Failed to get response from Gemini API", "details": response.text}), response.status_code

        result = response.json()
        ai_response = result.get("candidates", [{}])[0].get("output", "")

        logging.info(f"✅ Gemini API Response: {ai_response}")
        return jsonify({"response": ai_response})

    except Exception as e:
        logging.exception("💥 Exception occurred while calling Gemini API")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(port=8000, debug=True)
