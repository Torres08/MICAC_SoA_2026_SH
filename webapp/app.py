from flask import Flask, request, jsonify, render_template
from dependency_reader.main import run_analysis
from dotenv import load_dotenv
load_dotenv("dependency_reader/.env")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    repo_url = data.get("repo")

    if not repo_url:
        return jsonify({"error": "Missing repo URL"}), 400

    try:
        result = run_analysis(repo_url, save=False)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500