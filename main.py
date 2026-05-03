from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = "BURAYA_TOKEN"
URL = f"https://api.telegram.org/bot{TOKEN}"

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/ping")
def ping():
    return {"ping": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("DATA:", data)

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    reply = f"Mesajını aldım: {text}"

    r = requests.post(
        f"{URL}/sendMessage",
        json={"chat_id": chat_id, "text": reply},
        timeout=2
    )

    print("TELEGRAM:", r.text)

    return {"ok": True}
