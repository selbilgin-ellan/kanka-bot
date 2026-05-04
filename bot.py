import requests
import time

TOKEN = "8627427380:AAEicdo2m-_M0rJudt84CepHSlphwj8W79k"
URL = f"https://api.telegram.org/bot{TOKEN}"

last_update_id = None

def get_updates():
    global last_update_id

    params = {"timeout": 30}
    if last_update_id:
        params["offset"] = last_update_id + 1

    res = requests.get(f"{URL}/getUpdates", params=params).json()
    return res

def send_message(chat_id, text):
    requests.post(f"{URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

print("Bot çalışıyor...")

while True:
    data = get_updates()

    for update in data["result"]:
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
