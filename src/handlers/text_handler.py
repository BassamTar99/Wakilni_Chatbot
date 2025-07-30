import os
from telegram import Update
from telegram.ext import ContextTypes
import openai
from dotenv import load_dotenv
import json

# Import conversation store
from src.services.db_service import save_message, get_conversation

# Load OpenAI API key from .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FINE_TUNED_MODEL = os.getenv("OPENAI_FINE_TUNED_MODEL")
openai.api_key = OPENAI_API_KEY

async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = str(update.message.chat_id)
    print(f"[User message] {user_text}")  # Log the user's message

    # Save user message
    save_message(chat_id, "user", user_text)

    # Retrieve conversation history
    history = get_conversation(chat_id)

    # Build context-aware prompt for OpenAI
    messages = [{"role": "system", "content": "You are Wakilni’s support assistant, always follow the fine-tuning style."}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_text})

    try:
        print(f"▶️ Using OpenAI model: {FINE_TUNED_MODEL!r}")
        response = openai.chat.completions.create(
            model=FINE_TUNED_MODEL,
            messages=messages,
            temperature=0
        )
        ai_reply = response.choices[0].message.content.strip()

        # Save bot reply
        save_message(chat_id, "assistant", ai_reply)

        # Try to parse a Jira ticket payload
        try:
            payload = json.loads(ai_reply)
            if "create_issue" in payload:
                ci = payload["create_issue"]
                # Import create_jira_issue from services (to be implemented)
                from src.services.jira_service import create_jira_issue
                key = create_jira_issue(
                    ci["summary"],
                    ci["description"],
                    issuetype=ci.get("issuetype", "Task"),
                    project_key=ci.get("project_key", "WC")
                )
                await update.message.reply_text(f"✅ Created ticket {key}! Our team will follow up shortly.")
                return
        except Exception:
            pass

        await update.message.reply_text(ai_reply)
    except Exception as e:
        await update.message.reply_text(f"[AI error] {str(e)}")
    
# Simple router for incoming text
from src.handlers.analyse_handler import handle_analysis

def handle_text(chat_id: str, text: str) -> str:
    if text.startswith('/help'):
        from src.handlers.help_handler import handle_help
        return handle_help(chat_id)
    elif text.startswith('/track'):
        order_id = text.split(' ', 1)[-1] if ' ' in text else None
        if order_id:
            return f"Tracking order {order_id}: Status is 'In Transit'."
        else:
            return "Please provide an order ID. Usage: /track <order_id>"
    elif text.startswith('/cancel'):
        order_id = text.split(' ', 1)[-1] if ' ' in text else None
        if order_id:
            return f"Order {order_id} has been cancelled."
        else:
            return "Please provide an order ID. Usage: /cancel <order_id>"
    elif text.startswith('/status'):
        order_id = text.split(' ', 1)[-1] if ' ' in text else None
        if order_id:
            return f"Order {order_id} status: Delivered."
        else:
            return "Please provide an order ID. Usage: /status <order_id>"
    else:
        return handle_analysis(chat_id, text)
