

from fastapi import APIRouter, Request, Response, status
import os
import time
import requests
import json

# Import services for conversation tracking and AI
from src.services.db_service import save_message, get_history
from src.services.ai_analysis import build_engineering_prompt, call_openai_agent

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

telegram_router = APIRouter()

@telegram_router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    # 1. Parse incoming JSON from Telegram
    data = await request.json()
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    user_id = str(data.get("message", {}).get("from", {}).get("id"))
    text = data.get("message", {}).get("text")
    timestamp = data.get("message", {}).get("date", int(time.time()))

    print(f"[Webhook] chat_id={chat_id} user_id={user_id} text={text}")

    # 2. Save the user message to the conversation history
    save_message(str(user_id), "user", text, timestamp)

    # 3. Retrieve conversation history for context-aware AI
    history = get_history(str(user_id))

    # 4. Build the engineering prompt for OpenAI
    messages = build_engineering_prompt(text, history)

    # 5. Call OpenAI to get the AI's reply
    ai_reply = call_openai_agent(messages)

    # 6. Parse the JSON and extract the 'suggestion' field only
    try:
        reply_text = json.loads(ai_reply)["suggestion"]
    except Exception:
        reply_text = ai_reply

    # 8. Save the bot reply to the conversation history
    save_message(str(user_id), "assistant", reply_text, int(time.time()))

    # 9. Send the reply to the user via Telegram API
    if chat_id:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply_text
        })

    # 10. Return HTTP 200 immediately to Telegram
    return Response(status_code=status.HTTP_200_OK)

