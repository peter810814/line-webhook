from flask import Flask, request, jsonify
import os
import requests
import logging

app = Flask(__name__)

# === 設定 Logging ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)

# === 環境變數區 ===
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

if not LINE_ACCESS_TOKEN or not GROUP_ID:
    logging.error("❌ LINE_ACCESS_TOKEN 或 GROUP_ID 環境變數尚未設定，請至 Railway 設定 Variables")
    exit(1)

# === Webhook 主邏輯 ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    image_url = data.get("image_url")

    logging.info("📨 收到 POST 請求，內容如下：")
    logging.info(data)

    if not image_url:
        logging.warning("⚠️ 未提供 image_url")
        return jsonify({"error": "No image_url provided"}), 400

    # LINE API 請求
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

    logging.info(f"📤 傳送圖片至 LINE 群組，圖片網址為：{image_url}")
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

    if res.status_code == 200:
        logging.info("✅ LINE 發送成功")
        return jsonify({"status": "success"}), 200
    else:
        logging.error(f"❌ LINE 發送失敗，錯誤內容：{res.text}")
        return jsonify({"status": "fail", "error": res.json()}), 500

# === 健康檢查 ===
@app.route("/", methods=["GET"])
def index():
    return "✅ LINE Webhook is running."

# === 執行 Web Server ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
