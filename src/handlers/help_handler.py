from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me any message and I'll try to help! Use /analyse for analysis.")

def handle_help(chat_id: str) -> str:
    return (
        "Hi! I can help you:\n"
        "- Report an issue (just type your problem)\n"
        "- Get FAQs (/faq)\n"
        "- Track your order (/track 12345)\n"
        "- Cancel an order (/cancel 12345)\n"
        "… and more!"
    )
