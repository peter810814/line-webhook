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

# === 環境變數 ===
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

if not LINE_ACCESS_TOKEN or not GROUP_ID:
    logging.error("❌ 請確認環境變數 LINE_ACCESS_TOKEN 與 GROUP_ID 是否正確設定")
    exit(1)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logging.info("📨 收到 POST 請求，內容如下：")
    logging.info(data)

    # ✅ 印出來自群組的 groupId（僅供取得使用）
    source = data.get("events", [{}])[0].get("source", {})
    group_id = source.get("groupId")
    if group_id:
        logging.info(f"📌 偵測到群組 ID：{group_id}")

    # ✅ 處理圖片推送請求（test.py 用）
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

    logging.info(f"📤 傳送圖片至 LINE 群組，圖片網址為：{image_url}")
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)

    if res.status_code == 200:
        logging.info("✅ LINE 發送成功")
        return jsonify({"status": "success"}), 200
    else:
        logging.error(f"❌ LINE 發送失敗，錯誤內容：{res.text}")
        return jsonify({"status": "fail", "error": res.json()}), 500

@app.route("/", methods=["GET"])
def index():
    return "✅ LINE Webhook is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
