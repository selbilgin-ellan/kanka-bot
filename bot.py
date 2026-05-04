import requests
import time
import threading
from fastapi import FastAPI
import uvicorn
import json
from datetime import datetime, timedelta

TOKEN = "8627427380:AAEicdo2m-_M0rJudt84CepHSlphwj8W79k"
URL = f"https://api.telegram.org/bot{TOKEN}"

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
/stok
/sorgu
/liste
/kritik
/ekle
/bugun
/sayac dakika açıklama
/sayaclar"""

    # ⏰ KALICI SAYAÇ
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

    # 📋 AKTİF SAYAÇLAR
    if text.startswith("/sayaclar"):
        data = load_data()

        if "sayaclar" not in data or not data["sayaclar"]:
            return "Aktif sayaç yok"

        cevap = "AKTİF SAYAÇLAR:\n"

        for s in data["sayaclar"]:
            if not s["gonderildi"]:
                bitis = datetime.fromisoformat(s["bitis"])
                kalan = bitis - datetime.now()
                dakika = int(kalan.total_seconds() / 60)

                cevap += f"{s['mesaj']} → {dakika} dk kaldı\n"

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
# SAYAÇ KONTROL
# =====================

def sayac_kontrol():
    while True:
        data = load_data()

        if "sayaclar" in data:
            for s in data["sayaclar"]:
                if not s["gonderildi"]:
                    bitis = datetime.fromisoformat(s["bitis"])

                    if datetime.now() >= bitis and not s["gonderildi"]:
                        s["gonderildi"] = True

                            data["alarm"] = True
                            save_data(data)

                            def alarm_baslat(chat_id, mesaj):
                                while True:
                                    data = load_data()
                                if not data.get("alarm"):
                                    break

                                    send_message(chat_id, f"⏰ ALARM: {mesaj}")
                                        time.sleep(3)

                                        threading.Thread(target=alarm_baslat, args=(s["chat_id"], s["mesaj"])).start()e

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
# WEB
# =====================

@app.get("/")
def home():
    return {"status": "ok"}


# =====================
# RUN
# =====================

if __name__ == "__main__":
    threading.Thread(target=bot_loop).start()
    threading.Thread(target=sayac_kontrol).start()
    uvicorn.run(app, host="0.0.0.0", port=8080)
