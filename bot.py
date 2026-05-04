import requests
import time
import threading
from fastapi import FastAPI
import uvicorn
import json

TOKEN = "8627427380:AAEicdo2m-_M0rJudt84CepHSlphwj8W79k"
URL = f"https://api.telegram.org/bot{TOKEN}"

app = FastAPI()
last_update_id = 0


# =====================
# DATA (hafıza)
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
# KOMUT SİSTEMİ
# =====================

def handle_command(text):
    parts = text.strip().split()

    if text.startswith("/start"):
        return "Komutlar:\n/stok urun adet\n/sorgu urun\n/liste"

    if text.startswith("/stok"):
        if len(parts) >= 3:
            urun = parts[1]
            adet = int(parts[2])

            data = load_data()
            data[urun] = data.get(urun, 0) + adet
            save_data(data)

            return f"{urun} stok: {data[urun]}"
        return "Kullanım: /stok urun adet"

    if text.startswith("/sorgu"):
        if len(parts) >= 2:
            urun = parts[1]

            data = load_data()
            adet = data.get(urun, 0)

            return f"{urun} stok: {adet}"
        return "Kullanım: /sorgu urun"

    # 🔥 YENİ EKLENEN ÖZELLİK
    if text.startswith("/liste"):
        data = load_data()

        if not data:
            return "Stok boş"

        cevap = "STOK DURUMU:\n"
        for urun, adet in data.items():
            cevap += f"{urun}: {adet}\n"

        return cevap

    return None


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
            print("HATA:", data)
            return {"result": []}

        return data

    except Exception as e:
        print("ERROR:", e)
        return {"result": []}


def send_message(chat_id, text):
    try:
        requests.post(f"{URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": text
        })
    except Exception as e:
        print("SEND ERROR:", e)


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

            print("Mesaj:", text)

            reply = handle_command(text)

            if not reply:
                reply = f"Mesajını aldım: {text}"

            send_message(chat_id, reply)

        time.sleep(1)


# =====================
# WEB SERVER (Railway için)
# =====================

@app.get("/")
def home():
    return {"status": "ok"}


# =====================
# RUN
# =====================

if __name__ == "__main__":
    threading.Thread(target=bot_loop).start()
    uvicorn.run(app, host="0.0.0.0", port=8080)
