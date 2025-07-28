

from fastapi import APIRouter, Request, Response, status
import os
import time
import requests
import json

# Import services for conversation tracking and AI
from src.services.db_service import save_message, get_history
from src.services.ai_analysis import build_engineering_prompt, call_openai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

telegram_router = APIRouter()

@telegram_router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    # 1. Parse incoming JSON from Telegram
    data = await request.json()
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    user_id = data.get("message", {}).get("from", {}).get("id")
    text = data.get("message", {}).get("text")
    timestamp = data.get("message", {}).get("date", int(time.time()))

    print(f"[Webhook] chat_id={chat_id} user_id={user_id} text={text}")

    # 2. Save the user message to the conversation history
    save_message(user_id, "user", text, timestamp)

    # 3. Retrieve conversation history for context-aware AI
    history = get_history(user_id)

    # 4. Build the engineering prompt for OpenAI
    messages = build_engineering_prompt(text, history)

    # 5. Call OpenAI to get the AI's reply
    ai_reply = call_openai(messages)

    # 6. Try to parse the AI reply as JSON for ticket creation
    ticket_created = False
    ticket_key = None
    reply_text = ai_reply
    try:
        payload = json.loads(ai_reply)
        if "create_issue" in payload:
            ci = payload["create_issue"]
            # Here you would call your Jira service to create a ticket
            # from src.services.jira_service import create_jira_issue
            # ticket_key = create_jira_issue(ci["summary"], ci["description"], ci.get("issuetype", "Task"))
            ticket_key = "WC-123"  # Stub for demonstration
            ticket_created = True
    except Exception:
        pass

    # 7. Prepare the bot's reply
    if ticket_created:
        reply_text = f"✅ Created ticket {ticket_key}! Our team will follow up shortly."

    # 8. Save the bot reply to the conversation history
    save_message(user_id, "bot", reply_text, int(time.time()))

    # 9. Send the reply to the user via Telegram API
    if chat_id:
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply_text
        })

    # 10. Return HTTP 200 immediately to Telegram
    return Response(status_code=status.HTTP_200_OK)

