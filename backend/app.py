# --- third-party ---
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- local ---
from rag import ask

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

MAX_QUESTION_LENGTH = 500


@app.post("/api/ask")
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
    app.run(port=5000, debug=True)