# --- stdlib ---
import os

# --- third-party ---
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- local ---
from rag import ask

app = Flask(__name__)

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
CORS(app, origins=ALLOWED_ORIGINS)


def client_ip() -> str:
    return request.headers.get("X-Real-IP") or get_remote_address()


limiter = Limiter(
    key_func=client_ip,
    app=app,
    storage_uri="memory://",
)

@app.errorhandler(429)
def too_many_requests(_error):
    return jsonify({"error": "Too many questions. Please wait a minute and try again."}), 429


MAX_QUESTION_LENGTH = 500

@app.post("/api/ask")
@limiter.limit("10 per minute;75 per day")
def ask_route():
    body = request.get_json(silent=True) or {}
    question = body.get("question")

    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Send a JSON body with a non-empty 'question' string."}), 400
    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({"error": f"Question must be {MAX_QUESTION_LENGTH} characters or fewer."}), 400

    try:
        result = ask(question.strip())
    except Exception:
        app.logger.exception("ask() failed")
        return jsonify({"error": "Something went wrong. Please try again."}), 500

    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")