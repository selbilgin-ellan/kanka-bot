from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN yok")

TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("DATA:", data)

    message = data.get("message") or data.get("edited_message") or data.get("channel_post") or {}

    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    print("CHAT_ID:", chat_id)

    if not chat_id:
        return {"ok": True}

    reply = f"Mesajını aldım: {text}"

    try:
        requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": reply
            }
        )
    except Exception as e:
        print("HATA:", e)

    return {"ok": True}
