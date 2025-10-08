from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)

# Ensure the API key is set
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")
openai.api_key = OPENAI_API_KEY

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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            max_tokens=300
        )
        reply = response.choices[0].message["content"].strip()

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
