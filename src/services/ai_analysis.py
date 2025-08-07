from dotenv import load_dotenv
load_dotenv()



import os

from openai import OpenAI
from typing import List, Dict, Any
import json

# Import tool wrappers and define schemas
from src.services.agent_tools import fetch_page, parse_requirements, run_diagnostics, lookup_faq, create_jira_issue

# Tool schemas for OpenAI function-calling
TOOL_SCHEMAS = [
    {
        "name": "fetch_page",
        "description": "Retrieve a documentation or error page by URL",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The full URL of the Wakilni documentation or error spec."}
            },
            "required": ["url"]
        }
    },
    {
        "name": "parse_requirements",
        "description": "Extract structured requirements from a docs page",
        "parameters": {
            "type": "object",
            "properties": {
                "html": {"type": "string", "description": "HTML content of the documentation page."}
            },
            "required": ["html"]
        }
    },
    {
        "name": "run_diagnostics",
        "description": "Hit an internal health-check or status API",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "lookup_faq",
        "description": "Query your FAQ vector store for top-n similar entries",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "FAQ search query."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_jira_issue",
        "description": "Open a new Jira ticket when an actionable problem is found",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "description": {"type": "string"},
                "priority": {"type": "string"}
            },
            "required": ["summary", "description", "priority"]
        }
    }
]

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


def call_openai_agent(messages: List[Dict]) -> str:
    """
    Call OpenAI with function-calling, handle tool calls, and return the final assistant reply.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    tool_map = {
        "fetch_page": fetch_page,
        "parse_requirements": parse_requirements,
        "run_diagnostics": run_diagnostics,
        "lookup_faq": lookup_faq,
        "create_jira_issue": create_jira_issue
    }
    while True:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            functions=TOOL_SCHEMAS,
            function_call="auto",
            temperature=0.2
        )
        msg = resp.choices[0].message
        if msg.function_call:
            fn_name = msg.function_call.name
            fn_args = json.loads(msg.function_call.arguments)
            fn = tool_map.get(fn_name)
            if fn:
                result = fn(**fn_args)
            else:
                result = {"error": f"Unknown tool: {fn_name}"}
            messages.append({
                "role": "function",
                "name": fn_name,
                "content": json.dumps(result)
            })
            continue  # Re-invoke with new function result
        # If no function call, return the assistant's reply
        return msg.content.strip() if msg.content else "[No reply]"

# Alias for compatibility with telegram.py
def build_engineering_prompt(user_input: str, conversation: List[Dict]) -> List[Dict]:
    return build_prompt(conversation, user_input)

