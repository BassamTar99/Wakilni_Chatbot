from dotenv import load_dotenv
load_dotenv()



import os
from openai import OpenAI
from typing import List, Dict

MODEL = os.getenv("OPENAI_FINE_TUNED_MODEL")  # ft:…Btd6MRY9

SYSTEM_PROMPT = (
    "You are Wakilni’s support assistant. Analyze user messages "
    "and either reply conversationally or output a JSON "
    "create_issue command for new problems."
)


def format_history(history: List[Dict]) -> str:
    lines = []
    for msg in history[-5:]:  # last 5 messages
        role = "User" if msg["role"] == "user" else "Bot"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)

def build_prompt(history: List[Dict], user_text: str) -> List[Dict]:
    system_content = (
        """
You are Wakilni’s Automated Support Assistant.
Given the conversation history and a new user message, you must choose exactly one of two JSON outputs—and nothing else:

1. Direct answer:
   Output a JSON object with a single key \"reply\", whose value is the text you’d send the user.

2. Ticket creation:
   Output a JSON object with a single key \"create_issue\", whose value is another object containing:
     • summary: a 1-line summary
     • description: full details
     • issuetype: e.g. \"Task\"
     • priority: one of \"P0\", \"P1\", \"P2\", or \"P3\"

IMPORTANT:
• Output must be valid JSON (no extra keys, no markdown, no prose).
• Do not ask follow-up questions.
• Do not wrap the JSON in backticks or quotes.
"""
    )
    user_content = f"""
Conversation history:
{format_history(history)}

New request:
{user_text}
"""
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]

def call_openai(messages: List[Dict]) -> str:
    """
    Send to OpenAI and return the assistant’s reply using the new OpenAI API client.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

# Alias for compatibility with telegram.py
def build_engineering_prompt(user_input: str, conversation: List[Dict]) -> List[Dict]:
    return build_prompt(conversation, user_input)

