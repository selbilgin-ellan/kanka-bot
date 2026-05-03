from fastapi import FastAPI, Request, BackgroundTasks
import requests

app = FastAPI()

TOKEN = "BURAYA_TOKEN"
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    try:
        requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=5
        )
    except Exception as e:
        print("ERROR:", e)

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print("DATA:", data)

    message = (
        data.get("message")
        or data.get("edited_message")
        or data.get("channel_post")
    )

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    reply = f"Mesajını aldım: {text}"

    # 🔥 KRİTİK NOKTA
    background_tasks.add_task(send_message, chat_id, reply)

    return {"ok": True}
