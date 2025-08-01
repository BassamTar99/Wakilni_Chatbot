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
    from src.services.ai_analysis import build_prompt, call_openai
    messages = build_prompt(history, user_text)

    try:
        print(f"▶️ Using OpenAI model: {FINE_TUNED_MODEL!r}")
        ai_reply = call_openai(messages)

        # Parse structured output
        try:
            payload = json.loads(ai_reply)
            language = payload.get("language")
            category = payload.get("category")
            suggestion = payload.get("suggestion")
            resolution = payload.get("resolution")
            escalation_flag = payload.get("escalation_flag")
            confidence_score = payload.get("confidence_score")
            jira_ticket_key = None
            if payload.get("create_issue"):
                ci = payload["create_issue"]
                from src.services.jira_service import create_jira_issue
                key = create_jira_issue(
                    ci["summary"],
                    ci["description"],
                    issuetype=ci.get("issuetype", "Task"),
                    project_key=ci.get("project_key", "WC")
                )
                jira_ticket_key = key
                bot_reply = f"✅ Created ticket {key}! Our team will follow up shortly.\nSuggestion: {suggestion or ''}"
            elif payload.get("resolution"):
                bot_reply = f"{payload['resolution']}\nSuggestion: {suggestion or ''}"
            else:
                bot_reply = suggestion or ai_reply
        except Exception:
            # Fallback to raw reply if parsing fails
            language = category = suggestion = resolution = escalation_flag = confidence_score = jira_ticket_key = None
            bot_reply = ai_reply

        # Save bot reply with analysis
        save_message(
            chat_id,
            "assistant",
            bot_reply,
            ai_analysis=ai_reply,
            jira_ticket_key=jira_ticket_key,
            language=language,
            category=category,
            suggestion=suggestion,
            resolution=resolution,
            escalation_flag=escalation_flag,
            confidence_score=confidence_score
        )

        await update.message.reply_text(bot_reply)
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
