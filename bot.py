import os
from pathlib import Path
from dotenv import load_dotenv
# Import all necessary telegram/ext terms
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Add missing telegram imports
from telegram import Update
from telegram.ext import ContextTypes

# Add missing imports for bot application and handlers
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 1. Point to your .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# 2. Pull them in
JIRA_EMAIL  = os.getenv("JIRA_EMAIL")
JIRA_TOKEN  = os.getenv("JIRA_TOKEN")
JIRA_SERVER = os.getenv("JIRA_SERVER")

# Add TELEGRAM_TOKEN from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# 3. Debug-print what was loaded
print("🔑 JIRA_EMAIL: ",      repr(JIRA_EMAIL))
print("🔑 JIRA_TOKEN starts:", repr(JIRA_TOKEN)[:10], "…")
print("🔑 JIRA_SERVER:",      repr(JIRA_SERVER))

# 4. Fail early if any are missing
for var_name, val in [("JIRA_EMAIL", JIRA_EMAIL),
                      ("JIRA_TOKEN", JIRA_TOKEN),
                      ("JIRA_SERVER", JIRA_SERVER)]:
    if not val:
        raise RuntimeError(f"❌ Missing env var: {var_name}")

# Initialize Jira client

from jira import JIRA
jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_EMAIL, JIRA_TOKEN))



# Import handlers from new src.handlers location
from src.handlers.help_handler import help_command
from src.handlers.analyse_handler import handle_analysis
from src.handlers.text_handler import text_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi there!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyse", handle_analysis))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()
