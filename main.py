from fastapi import FastAPI, Request, BackgroundTasks
import requests
import os

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    try:
        response = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            }
        )
        print("TELEGRAM RESPONSE:", response.text)
    except Exception as e:
        print("HATA:", e)

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()

    print("DATA:", data)

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return {"ok": True}

    reply = f"Mesajını aldım: {text}"

    background_tasks.add_task(send_message, chat_id, reply)

    return {"ok": True}
