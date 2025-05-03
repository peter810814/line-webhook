import os
import time
import base64
import pyautogui
import requests
import pygetwindow as gw
from datetime import datetime
from PIL import Image
import subprocess

# === 設定 ===
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GROUP_ID = os.getenv("LINE_GROUP_ID")

today_str = datetime.today().strftime('%Y-%m-%d')
EXCEL_FILE_PATH = fr'C:\Users\NeREuS\OneDrive\桌面\新進出港班表_處理完成_{today_str}.xlsx'

# === 尋找 Excel 執行檔 ===
def find_excel():
    paths = [
        r'C:\Program Files (x86)\Microsoft Office\Office14\EXCEL.EXE',
        r'C:\Program Files\Microsoft Office\Office14\EXCEL.EXE',
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

# === 裁切儲存格畫面 ===
def crop_excel_content(image_path, top_crop=130, bottom_crop=50):
    image = Image.open(image_path)
    width, height = image.size
    cropped = image.crop((0, top_crop, width, height - bottom_crop))
    cropped.save(image_path)

# === 關閉 Excel 視窗（不儲存）===
def close_excel():
    for w in gw.getWindowsWithTitle('Excel'):
        if w.visible:
            w.activate()
            time.sleep(1)
            pyautogui.hotkey('alt', 'f4')
            time.sleep(1)
            pyautogui.press('n')
            return

# === 主流程 ===
def main():
    excel_exe = find_excel()
    if not excel_exe:
        print("❌ 找不到 Excel")
        return

    subprocess.Popen([excel_exe, EXCEL_FILE_PATH])
    time.sleep(7)

    excel_window = next((w for w in gw.getWindowsWithTitle('Excel') if w.visible), None)
    if not excel_window:
        print("❌ Excel 視窗未開啟")
        return

    excel_window.activate()
    excel_window.maximize()
    time.sleep(2)

    left, top, width, height = excel_window.left, excel_window.top, excel_window.width, excel_window.height
    screenshot = pyautogui.screenshot(region=(left, top, width, height))

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    image_name = f"excel_{timestamp}.png"
    image_path = os.path.join(os.path.expanduser('~'), 'Downloads', image_name)
    screenshot.save(image_path)
    crop_excel_content(image_path)

    with open(image_path, 'rb') as img_file:
        b64_image = base64.b64encode(img_file.read())

    headers_imgur = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
    res = requests.post('https://api.imgur.com/3/image', headers=headers_imgur, data={'image': b64_image})

    if res.status_code != 200:
        print("❌ Imgur 上傳失敗")
        return

    imgur_url = res.json()['data']['link']

    headers_line = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    line_data = {
        'to': GROUP_ID,
        'messages': [{
            'type': 'image',
            'originalContentUrl': imgur_url,
            'previewImageUrl': imgur_url
        }]
    }
    line_res = requests.post('https://api.line.me/v2/bot/message/push', headers=headers_line, json=line_data)
    print("📤 已推送至 LINE 群組" if line_res.status_code == 200 else f"❌ LINE 發送失敗：{line_res.text}")

    close_excel()

if __name__ == "__main__":
    main()
