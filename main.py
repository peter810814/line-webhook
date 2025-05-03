from flask import Flask, request, jsonify
import os
import requests
import logging

app = Flask(__name__)

# 啟用 Logging（可在 Railway Logs 中查看）
logging.basicConfig(level=logging.INFO)

# 讀取 LINE 的環境變數（請在 Railway 設定環境變數）
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logging.info("📨 收到 POST 請求，內容如下：")
    logging.info(data)

    # ✅ 如果是來自 LINE webhook 的事件（LINE 驗證 or 訊息觸發）
    if "events" in data:
        source = data.get("events", [{}])[0].get("source", {})
        group_id = source.get("groupId")
        if group_id:
            logging.info(f"📌 偵測到群組 ID：{group_id}")
        return jsonify({"status": "received LINE webhook"}), 200

    # ✅ 否則為 image_url 傳圖邏輯
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
    return "✅ Railway Webhook Ready"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
