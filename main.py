from fastapi import FastAPI, Request, BackgroundTasks
import requests

app = FastAPI()

TOKEN = "8674979192:AAFn5OYVVOF4qH96To3GEvwwUkt-VslS9k8"
URL = f"https://api.telegram.org/bot{TOKEN}"

def send_message(chat_id, text):
    try:
        requests.post(
            f"{URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=5
        )
    except Exception as e:
        print("ERROR:", e)

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    print("DATA:", data)

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    reply = f"Mesajını aldım: {text}"

    # 🔥 EN KRİTİK SATIR
    background_tasks.add_task(send_message, chat_id, reply)

    return {"ok": True}
