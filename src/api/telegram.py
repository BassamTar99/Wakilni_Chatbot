from fastapi import APIRouter, Request, Response, status, FastAPI
from fastapi.responses import JSONResponse
import os
import time
import requests
import json

# --- JIRA Webhook Router ---
jiraweb_router = APIRouter()

from src.services.db_engine import SessionLocal
from src.services.models import Message, Conversation

def lookup_chat_id_by_issue_key(issue_key: str):
    db = SessionLocal()
    msg = db.query(Message).filter_by(jira_ticket_key=issue_key).first()
    if msg:
        conv = db.query(Conversation).filter_by(id=msg.conversation_id).first()
        db.close()
        return conv.user_id if conv else None
    db.close()
    return None

def send_telegram_message(chat_id: str, text: str):
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(BASE_URL, json=payload)
    print(f"Telegram send status: {resp.status_code}, response: {resp.text}")
    try:
        print("Telegram API response JSON:", resp.json())
    except Exception as e:
        print("Failed to parse Telegram API response as JSON:", e)

@jiraweb_router.post("/api/jira/webhook")
async def jiraweb(request: Request):
    data = await request.json()
    print("Received JIRA webhook:", data)

    # --- Handle comment created event ---
    if 'comment' in data:
        issue = data.get('issue', {})
        issue_key = issue.get('key', '')
        comment = data['comment']
        comment_body = comment.get('body', '')
        author = comment.get('author', {}).get('displayName', 'Staff')
        print(f"[JIRA webhook] Extracted issue_key: {issue_key}")
        chat_id = lookup_chat_id_by_issue_key(issue_key)
        print(f"[JIRA webhook] chat_id lookup result: {chat_id}")
        if chat_id:
            print(f"[JIRA webhook] Sending Telegram message: {comment_body}")
            send_telegram_message(chat_id, comment_body)
        else:
            print(f"[JIRA webhook] No chat_id found for issue {issue_key}")

    # --- Optionally, handle issue transitioned to Done ---
    issue = data.get('issue', {})
    fields = issue.get('fields', {})
    status = fields.get('status', {}).get('name', '').lower()
    issue_key = issue.get('key', '')
    print(f"[JIRA webhook] Status for issue {issue_key}: {status}")
    if status == 'done':
        print(f"[JIRA webhook] Issue {issue_key} marked as Done. Sending completion message to client...")
        completion_msg = "✅ All is done! Don't hesitate to reach out if you face any issue in the future."
        chat_id = lookup_chat_id_by_issue_key(issue_key)
        print(f"[JIRA webhook] chat_id lookup result for Done: {chat_id}")
        if chat_id:
            print(f"[JIRA webhook] Sending Telegram message: {completion_msg}")
            send_telegram_message(chat_id, completion_msg)
        else:
            print(f"[JIRA webhook] No chat_id found for issue {issue_key}")
    return JSONResponse({"status": "received"})

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
    # Save assistant message and get its DB id for mapping
    db = SessionLocal()
    conv = db.query(Conversation).filter_by(user_id=str(user_id), is_active=True).first()
    conversation_id = conv.id if conv else None
    assistant_msg = None
    if conversation_id:
        # Save the assistant message
        save_message(str(user_id), "assistant", reply_text, int(time.time()))
        # Fetch the latest assistant message for this conversation
        assistant_msg = db.query(Message).filter_by(sender="assistant", conversation_id=conversation_id).order_by(Message.timestamp.desc()).first()
    db.close()

    if chat_id:
        print(f"Sending to Telegram: {reply_text}")
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply_text
        })

    # Use parsed payload for JIRA ticket creation and map JIRA issue key to conversation
    try:
        if 'payload' in locals() and payload and "create_issue" in payload and payload["create_issue"]:
            ci = payload["create_issue"]
            summary = ci.get("summary")
            description = ci.get("description")
            priority = ci.get("priority")
            # Check for duplicate/similar ticket in this conversation
            db = SessionLocal()
            # Get all previous tickets in this conversation
            previous_tickets = db.query(Message).filter(
                Message.conversation_id == conversation_id,
                Message.jira_ticket_key.isnot(None)
            ).all()
            found_duplicate = False
            for msg in previous_tickets:
                # Check similarity in summary or description (case-insensitive substring)
                prev_text = (msg.message_text or "").lower()
                if (summary and summary.lower() in prev_text) or (description and description.lower() in prev_text):
                    found_duplicate = True
                    duplicate = msg
                    break
            if found_duplicate:
                print(f"Similar JIRA ticket detected for summary '{summary}' or description '{description}' in conversation {conversation_id}. Skipping ticket creation.")
                # Optionally notify user
                if chat_id:
                    requests.post(f"{BASE_URL}/sendMessage", json={
                        "chat_id": chat_id,
                        "text": f"A ticket for this issue already exists: {duplicate.jira_ticket_key}"
                    })
                db.close()
            else:
                from src.services.agent_tools import create_jira_issue
                ticket_key = create_jira_issue(summary=summary, description=description, priority=priority)
                print(f"Jira ticket created: {ticket_key}")
                # Map JIRA issue key to the latest assistant message
                if assistant_msg:
                    msg = db.query(Message).get(assistant_msg.id)
                    # Always store the JIRA key as a string
                    if isinstance(ticket_key, dict) and "key" in ticket_key:
                        msg.jira_ticket_key = ticket_key["key"]
                    else:
                        msg.jira_ticket_key = str(ticket_key)
                    db.commit()
                    print(f"Mapped JIRA issue key {msg.jira_ticket_key} to message {msg.id}")
                else:
                    print("No assistant message found to map JIRA issue key.")
                db.close()
    except Exception as e:
        print(f"Exception during JIRA ticket creation: {e}")

    return Response(status_code=status.HTTP_200_OK)

## FastAPI app creation and router inclusion should only be done in main.py

