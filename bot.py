import requests
import time
import threading
from fastapi import FastAPI
import uvicorn
import json
import os
from datetime import datetime, timedelta

TOKEN = "BURAYA_TELEGRAM_TOKEN"
URL = f"https://api.telegram.org/bot{TOKEN}"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

app = FastAPI()
last_update_id = 0


# =====================
# DATA
# =====================

def load_data():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)


# =====================
# KOMUT
# =====================

def handle_command(text, chat_id):
    parts = text.strip().split()

    if text.startswith("/start"):
        return """Komutlar:
/sayac dakika açıklama
/sayaclar
/dur
/cevir metin"""

    # 🌍 PROFESYONEL ÇEVİRİ
    if text.startswith("/cevir"):
        content = text.replace("/cevir", "").strip()

        if not content:
            return "Kullanım: /cevir metin"

        deepl = deepl_translate(content)
        google = google_translate(content)
        best = ai_select_best(content, deepl, google)

        return f"""🌍 EN İYİ ÇEVİRİ:

{best}

--- kaynaklar ---

DeepL:
{deepl}

Google:
{google}
"""

    # ⏰ SAYAÇ KUR
    if text.startswith("/sayac"):
        parts = text.split(maxsplit=2)

        if len(parts) < 2:
            return "Kullanım: /sayac dakika açıklama"

        dakika = int(parts[1])
        mesaj = parts[2] if len(parts) > 2 else "Süre doldu"

        bitis = datetime.now() + timedelta(minutes=dakika)

        data = load_data()

        if "sayaclar" not in data:
            data["sayaclar"] = []

        data["sayaclar"].append({
            "chat_id": chat_id,
            "mesaj": mesaj,
            "bitis": bitis.isoformat(),
            "gonderildi": False
        })

        save_data(data)

        return f"{dakika} dk sayaç kuruldu"

    # 📋 SAYAÇLAR
    if text.startswith("/sayaclar"):
        data = load_data()

        if "sayaclar" not in data:
            return "Aktif sayaç yok"

        cevap = "AKTİF SAYAÇLAR:\n"

        for s in data["sayaclar"]:
            if not s["gonderildi"]:
                bitis = datetime.fromisoformat(s["bitis"])
                kalan = bitis - datetime.now()
                dakika = int(kalan.total_seconds() / 60)

                cevap += f"{s['mesaj']} → {dakika} dk kaldı\n"

        return cevap

    # 🔕 ALARMI DURDUR
    if text.startswith("/dur"):
        data = load_data()
        data["alarm"] = False
        save_data(data)
        return "Alarm durduruldu"

    return None


# =====================
# ÇEVİRİ MOTORLARI
# =====================

def deepl_translate(text):
    try:
        url = "https://api-free.deepl.com/v2/translate"

        params = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": "EN"
        }

        res = requests.post(url, data=params)
        return res.json()["translations"][0]["text"]

    except:
        return "DeepL hata"


def google_translate(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"

        params = {
            "client": "gtx",
            "sl": "tr",
            "tl": "en",
            "dt": "t",
            "q": text
        }

        res = requests.get(url, params=params)
        return res.json()[0][0][0]

    except:
        return "Google hata"


def ai_select_best(original, t1, t2):
    try:
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        prompt = f"""
Original text:
{original}

Translation 1:
{t1}

Translation 2:
{t2}

Choose the best translation and improve it if needed.
Return ONLY final version.
"""

        data = {
            "model": "gpt-4.1-mini",
            "messages": [{"role": "user", "content": prompt}]
        }

        res = requests.post(url, headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]

    except:
        return t1


# =====================
# TELEGRAM
# =====================

def get_updates():
    global last_update_id

    try:
        params = {
            "timeout": 30,
            "offset": last_update_id + 1
        }

        res = requests.get(f"{URL}/getUpdates", params=params)
        data = res.json()

        if not data.get("ok"):
            return {"result": []}

        return data

    except:
        return {"result": []}


def send_message(chat_id, text):
    requests.post(f"{URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })


# =====================
# ALARM
# =====================

def alarm_baslat(chat_id, mesaj):
    while True:
        data = load_data()

        if not data.get("alarm"):
            break

        send_message(chat_id, f"⏰ ALARM: {mesaj}")
        time.sleep(3)


def sayac_kontrol():
    while True:
        data = load_data()

        if "sayaclar" in data:
            for s in data["sayaclar"]:
                if not s["gonderildi"]:
                    bitis = datetime.fromisoformat(s["bitis"])

                    if datetime.now() >= bitis:
                        s["gonderildi"] = True
                        data["alarm"] = True
                        save_data(data)

                        threading.Thread(
                            target=alarm_baslat,
                            args=(s["chat_id"], s["mesaj"])
                        ).start()

            save_data(data)

        time.sleep(5)


# =====================
# BOT LOOP
# =====================

def bot_loop():
    global last_update_id
    print("Bot çalışıyor...")

    while True:
        data = get_updates()

        for update in data.get("result", []):
            last_update_id = update["update_id"]

            message = update.get("message")
            if not message:
                continue

            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            reply = handle_command(text, chat_id)

            if not reply:
                reply = "Komut gir. /start yaz"

            send_message(chat_id, reply)

        time.sleep(1)


# =====================
# RUN
# =====================

@app.get("/")
def home():
    return {"status": "ok"}


if __name__ == "__main__":
    threading.Thread(target=bot_loop).start()
    threading.Thread(target=sayac_kontrol).start()
    uvicorn.run(app, host="0.0.0.0", port=8080)
