
# --- Routers ---
from fastapi import APIRouter, Request, Response, status, FastAPI
from fastapi.responses import JSONResponse
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
debug_router = APIRouter()



@telegram_router.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    # ...existing code...
    data = await request.json()
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    user_id = str(data.get("message", {}).get("from", {}).get("id"))
    text = data.get("message", {}).get("text")
    timestamp = data.get("message", {}).get("date", int(time.time()))

    print(f"[Webhook] chat_id={chat_id} user_id={user_id} text={text}")

    save_message(str(user_id), "user", text, timestamp)
    history = get_history(str(user_id))
    messages = build_engineering_prompt(text, history)

    ai_reply = call_openai_agent(messages)
    print("Raw OpenAI response:", ai_reply)

    import re
    try:
        # Find the first complete JSON object using a balanced braces approach
        def find_first_json(s):
            start = s.find('{')
            if start == -1:
                return None
            depth = 0
            for i in range(start, len(s)):
                if s[i] == '{':
                    depth += 1
                elif s[i] == '}':
                    depth -= 1
                    if depth == 0:
                        return s[start:i+1]
            return None

        first_json = find_first_json(ai_reply)
        print(f"First complete JSON object: {first_json}")
        if first_json:
            payload = json.loads(first_json)
            print(f"Parsed payload: {payload}")
            reply_text = payload.get("suggestion", ai_reply)
            print(f"Extracted suggestion: {reply_text}")
        else:
            reply_text = ai_reply
            print(f"No JSON found, using raw AI reply: {reply_text}")
    except Exception as e:
        print(f"Exception during JSON parsing: {e}")
        reply_text = ai_reply

    print(f"Final reply_text to be sent: {reply_text}")
    save_message(str(user_id), "assistant", reply_text, int(time.time()))


    if chat_id:
        print(f"Sending to Telegram: {reply_text}")
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply_text
        })

    # Fix: Use parsed payload for JIRA ticket creation
    try:
        if 'payload' in locals() and payload and "create_issue" in payload and payload["create_issue"]:
            ci = payload["create_issue"]
            summary = ci.get("summary")
            description = ci.get("description")
            priority = ci.get("priority")
            from src.services.agent_tools import create_jira_issue
            ticket_key = create_jira_issue(summary=summary, description=description, priority=priority)
            print(f"Jira ticket created: {ticket_key}")
    except Exception as e:
        print(f"Exception during JIRA ticket creation: {e}")

    return Response(status_code=status.HTTP_200_OK)

# --- FastAPI app ---
app = FastAPI()
app.include_router(telegram_router)
app.include_router(debug_router)

