from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please enter a message."}), 400

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            max_tokens=200
        )
        reply = response.choices[0].message.content.strip()

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
