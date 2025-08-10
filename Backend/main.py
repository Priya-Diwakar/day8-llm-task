import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(api_version='v1alpha')
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to INFO in production
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = Flask(__name__)
CORS(app)


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
        return jsonify({"error": "Text input is required"}), 40

    logging.debug("🌐 Sending request to Gemini API")
    try:
        # response = requests.post(url, headers=headers, json=payload)
        response = client.models.generate_content(model='gemini-2.0-flash-001', contents=user_text)
        logging.debug(f"🔍 Raw Gemini API response: {response.text}")

        ai_response = response.text

        logging.info(f"✅ Gemini API Response: {ai_response}")
        return jsonify({"response": ai_response})

    except Exception as e:
        logging.exception("💥 Exception occurred while calling Gemini API")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(port=8000, debug=True)
