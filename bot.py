import requests
import time
import threading
from fastapi import FastAPI
import uvicorn

TOKEN = "SENIN_TOKEN"
URL = f"https://api.telegram.org/bot{TOKEN}"

app = FastAPI()
last_update_id = None

def get_updates():
    global last_update_id
    try:
        params = {"timeout": 30}
        if last_update_id:
            params["offset"] = last_update_id + 1

        res = requests.get(f"{URL}/getUpdates", params=params)
        data = res.json()

        if not data.get("ok"):
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

            reply = f"Mesajını aldım: {text}"
            send_message(chat_id, reply)

        time.sleep(1)

@app.get("/")
def home():
    return {"status": "ok"}

if __name__ == "__main__":
    threading.Thread(target=bot_loop).start()
    uvicorn.run(app, host="0.0.0.0", port=8080)
