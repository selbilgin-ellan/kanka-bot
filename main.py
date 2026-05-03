from fastapi import FastAPI, Request
import requests
import os

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

# SADECE SENİN ID'N (şimdilik boş bırakıyoruz)
OWNER_ID = 0

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/")
async def webhook(request: Request):
    data = await request.json()

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    # SADECE SEN KULLAN
    if chat_id != OWNER_ID:
        return {"ok": True}

    reply = f"Mesajını aldım: {text}"

    requests.post(f"{TELEGRAM_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    return {"ok": True}
