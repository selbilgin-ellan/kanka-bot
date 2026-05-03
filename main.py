from fastapi import FastAPI, Request
import requests

app = FastAPI()

TOKEN = "BURAYA_YENI_TOKEN"  # tırnak şart
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("DATA:", data)

        message = data.get("message")
        if not message:
            return {"ok": True}

        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        reply = f"Mesajını aldım: {text}"

        r = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": chat_id, "text": reply},
            timeout=5
        )
        print("TELEGRAM:", r.text)

    except Exception as e:
        print("ERROR:", str(e))

    return {"ok": True}
