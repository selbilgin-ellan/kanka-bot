import requests
import time
import threading
from fastapi import FastAPI
import uvicorn
import json
from datetime import datetime

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

def handle_command(text, chat_id):
    parts = text.strip().split()

    if text.startswith("/start"):
        return """Komutlar:
/stok urun adet
/sorgu urun
/liste
/kritik
/ekle yapılacak iş
/bugun
/sayac dakika açıklama"""

    # 📦 STOK EKLE
    if text.startswith("/stok"):
        if len(parts) >= 3:
            urun = parts[1]
            adet = int(parts[2])

            data = load_data()
            data[urun] = data.get(urun, 0) + adet
            save_data(data)

            return f"{urun} stok: {data[urun]}"
        return "Kullanım: /stok urun adet"

    # 📦 STOK SORGULA
    if text.startswith("/sorgu"):
        if len(parts) >= 2:
            urun = parts[1]

            data = load_data()
            adet = data.get(urun, 0)

            return f"{urun} stok: {adet}"
        return "Kullanım: /sorgu urun"

    # 📦 TÜM STOK
    if text.startswith("/liste"):
        data = load_data()

        if not data:
            return "Stok boş"

        cevap = "STOK DURUMU:\n"
        for urun, adet in data.items():
            if urun != "ajanda":
                cevap += f"{urun}: {adet}\n"

        return cevap

    # ⚠️ KRİTİK STOK
    if text.startswith("/kritik"):
        data = load_data()

        kritikler = []

        for urun, adet in data.items():
            if urun != "ajanda" and isinstance(adet, int) and adet < 50:
                kritikler.append(f"{urun}: {adet}")

        if not kritikler:
            return "Kritik stok yok"

        cevap = "KRİTİK STOK:\n"
        for k in kritikler:
            cevap += k + "\n"

        return cevap

    # 📅 AJANDA EKLE
    if text.startswith("/ekle"):
        content = text.replace("/ekle", "").strip()

        if not content:
            return "Kullanım: /ekle yapılacak iş"

        data = load_data()
        today = datetime.now().strftime("%Y-%m-%d")

        if "ajanda" not in data:
            data["ajanda"] = {}

        if today not in data["ajanda"]:
            data["ajanda"][today] = []

        data["ajanda"][today].append(content)
        save_data(data)

        return f"Bugüne eklendi: {content}"

    # 📅 BUGÜNÜ GÖR
    if text.startswith("/bugun"):
        data = load_data()
        today = datetime.now().strftime("%Y-%m-%d")

        if "ajanda" not in data or today not in data["ajanda"]:
            return "Bugün için kayıt yok"

        cevap = f"BUGÜN ({today}):\n"
        for i, item in enumerate(data["ajanda"][today], 1):
            cevap += f"{i}. {item}\n"

        return cevap

    # ⏰ GERİ SAYIM
    if text.startswith("/sayac"):
        parts = text.split(maxsplit=2)

        if len(parts) < 2:
            return "Kullanım: /sayac dakika açıklama"

        dakika = int(parts[1])
        mesaj = parts[2] if len(parts) > 2 else "Süre doldu"

        def hatirlat(chat_id, dakika, mesaj):
            time.sleep(dakika * 60)
            send_message(chat_id, f"⏰ SÜRE DOLDU: {mesaj}")

        threading.Thread(target=hatirlat, args=(chat_id, dakika, mesaj)).start()

        return f"{dakika} dakika geri sayım başladı: {mesaj}"

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

            reply = handle_command(text, chat_id)

            if not reply:
                reply = "Komut gir. /start yaz"

            send_message(chat_id, reply)

        time.sleep(1)


# =====================
# WEB SERVER
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
