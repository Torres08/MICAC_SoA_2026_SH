import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# In Docker: SCANNER_API=http://backend:8000/zombie-scan (set in docker-compose.yml)
# Locally:   falls back to 127.0.0.1 for direct python app.py usage
SCANNER_API = os.environ.get("SCANNER_API", "http://127.0.0.1:8000/zombie-scan")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    repo = request.json.get("repo")

    try:
        response = requests.post(
            SCANNER_API,
            json={"repo_url": repo},
            timeout=int(os.environ.get("SCANNER_TIMEOUT", 600))
        )

        return jsonify(response.json())

    except Exception:
        return jsonify({"error": "Scanner API unreachable"}), 500