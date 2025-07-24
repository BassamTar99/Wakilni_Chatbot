from telegram import Update
from telegram.ext import ContextTypes

async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Fallback: echo or connect to AI later
    await update.message.reply_text(f"You said: {user_text}")
