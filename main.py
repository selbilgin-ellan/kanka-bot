from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = "BURAYA_TOKEN"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("DATA:", data)

    message = data.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    print("CHAT_ID:", chat_id)

    reply = f"Mesajını aldım: {text}"

    try:
        r = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
            timeout=5
        )
        print("TELEGRAM:", r.text)
    except Exception as e:
        print("ERROR:", e)

    return {"ok": True}
