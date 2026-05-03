@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("DATA:", data)

    message = data.get("message") or data.get("edited_message") or data.get("channel_post") or {}

    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    print("CHAT_ID:", chat_id)

    reply = f"Mesajını aldım: {text}"

    requests.post(f"{TELEGRAM_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    return {"ok": True}
