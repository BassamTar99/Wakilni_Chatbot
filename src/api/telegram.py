
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

@debug_router.get("/debug/ai")
async def debug_ai_endpoint():
    from src.services.ai_analysis import build_engineering_prompt, call_openai_agent
    # Example static input
    user_input = "I have an issue with the communication... etc,"
    messages = build_engineering_prompt(user_input, [])
    ai_reply = call_openai_agent(messages)
    return JSONResponse(content={"input": user_input, "ai_reply": ai_reply})

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
        json_strings = re.findall(r'\{.*?\}', ai_reply, re.DOTALL)
        if json_strings:
            payload = json.loads(json_strings[0])
            reply_text = payload.get("suggestion", ai_reply)
        else:
            reply_text = ai_reply
    except Exception:
        reply_text = ai_reply

    save_message(str(user_id), "assistant", reply_text, int(time.time()))

    if chat_id:
        print(reply_text)
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": reply_text
        })

    try:
        if json_strings:
            payload = json.loads(json_strings[0])
            if "create_issue" in payload and payload["create_issue"]:
                ci = payload["create_issue"]
                summary = ci.get("summary")
                from src.services.agent_tools import create_jira_issue
                ticket_key = create_jira_issue(summary=summary)
                print(f"Jira ticket created: {ticket_key}")
    except Exception:
        pass

    return Response(status_code=status.HTTP_200_OK)

# --- FastAPI app ---
app = FastAPI()
app.include_router(telegram_router)
app.include_router(debug_router)

