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
For every user message, respond ONLY with a valid JSON object containing:

  - "language": detected language (English, Arabic, Arabizi, etc.)
  - "category": issue type (Delivery, AppBug, Payment, etc.)
  - "create_issue": object with Jira ticket details if needed, else null
      - summary: 1-line summary
      - description: full details
      - issuetype: e.g. "Task"
      - priority: "P0", "P1", "P2", or "P3"
  - "suggestion": advice or next steps for the user
  - "resolution": solution if the issue can be resolved without a ticket, else null
  - "escalation_flag": true if urgent, else false
  - "confidence_score": float between 0 and 1 for your confidence in categorization

If no ticket is needed, set "create_issue" to null.
If you can resolve the issue, fill "resolution" and set "suggestion" accordingly.
Do NOT include any extra keys, markdown, or prose. Output ONLY the JSON object.
Do NOT ask follow-up questions.
Do NOT wrap the JSON in backticks or quotes.
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

