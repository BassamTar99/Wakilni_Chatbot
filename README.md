# Wakilni AI Support System

## Overview

Wakilni AI Support System is an intelligent support automation platform that connects clients and staff via Telegram, automates ticket creation in JIRA, and leverages OpenAI for smart responses. The system is designed for seamless two-way communication, robust ticket management, and easy integration with enterprise tools.

## Architecture

- **Telegram Bot**: Handles user conversations and delivers support responses.
- **Core API (Python, FastAPI)**: Orchestrates logic between Telegram, JIRA, OpenAI, and the database.
- **PostgreSQL Database**: Stores conversations, messages, and ticket mappings.
- **OpenAI API**: Powers AI-driven suggestions and replies.
- **JIRA REST API**: Manages ticket creation and forwards staff comments/status updates to clients.

## Features

- **Telegram Integration**: Users interact with the bot for support; staff can reply via JIRA.
- **Automated JIRA Ticketing**: Issues are analyzed and tickets are created automatically.
- **Two-way Communication**: Staff comments and ticket status changes in JIRA are sent to clients via Telegram.
- **Duplicate Ticket Prevention**: The system checks for similar issues in the same conversation and avoids creating duplicate tickets.
- **Database Mapping**: Each JIRA ticket is mapped to the correct Telegram conversation for accurate notifications.
- **Debug Logging**: Extensive debug output for troubleshooting and monitoring.

## File Structure

| Component         | Main File(s)                        | Description                        |
|-------------------|-------------------------------------|------------------------------------|
| Telegram Bot      | `src/api/telegram.py`               | Telegram webhook, message handling |
| Core API          | `src/api/telegram.py`, `src/main.py`, `src/services/agent_tools.py`, `src/services/ai_analysis.py`, `src/services/db_service.py` | API logic, routing, integrations   |
| Database          | `src/services/db_engine.py`, `src/services/models.py` | SQLAlchemy engine/models           |
| OpenAI API        | `src/services/ai_analysis.py`       | AI prompt and response logic       |
| JIRA REST API     | `src/services/agent_tools.py`, `src/api/telegram.py` | Ticket creation, webhook handling  |

## How It Works

1. **User sends a message via Telegram.**
2. **Core API analyzes the message using OpenAI.**
3. **If an issue is detected, a JIRA ticket is created (unless a similar ticket already exists).**
4. **JIRA webhook forwards staff comments and status changes to the correct Telegram user.**
5. **All interactions are logged and mapped in the PostgreSQL database.**

## Getting Started

1. **Clone the repository.**
2. **Install dependencies:**  
   `pip install -r requirements.txt`
3. **Set up environment variables:**  
   Create a `.env` file in the project root with the following:
   ```env
   TELEGRAM_TOKEN=7549711377:AAF_lg1fH6d9cHNhOff63ffX_a32oXjYjXw
OPENAI_API_KEY=**************************************************************
OPENAI_FINE_TUNED_MODEL=ft:gpt-3.5-turbo-0125:personal::Btd6MRY9
JIRA_EMAIL=samotarshishi152005@gmail.com
JIRA_TOKEN=****************************************************
JIRA_SERVER=https://samotarshishi152005.atlassian.net
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wakilni_chatbot
DB_USER=postgres
DB_PASSWORD=Bwt152005.

   ```
4. **Run the FastAPI server:**  
   `uvicorn src.main:app --reload`
5. **Expose your server with ngrok for webhook testing:**  
   `ngrok http 8000`
6. **Configure Telegram and JIRA webhooks to point to your ngrok URL.**


