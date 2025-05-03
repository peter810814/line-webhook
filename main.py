# main.py
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "No image_url provided"}), 400

    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": GROUP_ID,
        "messages": [{
            "type": "image",
            "originalContentUrl": image_url,
            "previewImageUrl": image_url
        }]
    }

    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

    if res.status_code == 200:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "fail", "error": res.json()}), 500

@app.route("/", methods=["GET"])
def index():
    return "✅ Railway Webhook Ready"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
