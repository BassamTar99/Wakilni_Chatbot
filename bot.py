# Initialize Jira client
jira = JIRA(
    server=JIRA_SERVER,
    basic_auth=(JIRA_EMAIL, JIRA_TOKEN)
)

# Copilot: generate a function to create a Jira issue and return its key
def create_jira_issue(summary: str, description: str, issuetype: str = "Task", project_key: str = "WC") -> str:
    """
    Create a Jira issue and return its key.
    """
    issue_fields = {
        "project":     {"key": project_key},
        "summary":     summary,
        "description": description,
        "issuetype":   {"name": issuetype},
    }
    issue = jira.create_issue(fields=issue_fields)
    return issue.key
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Jira integration
from jira import JIRA

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Jira credentials
JIRA_EMAIL  = os.getenv("JIRA_EMAIL")
JIRA_TOKEN  = os.getenv("JIRA_TOKEN")
JIRA_SERVER = os.getenv("JIRA_SERVER")

# Initialize Jira client
jira = JIRA(
    server=JIRA_SERVER,
    basic_auth=(JIRA_EMAIL, JIRA_TOKEN)
)


# Import handlers
from handlers.help_handler import help_command
from handlers.analyse_handler import analyse_command
from handlers.text_handler import text_message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi there!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyse", analyse_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()
