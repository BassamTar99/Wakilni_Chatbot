

import os
import openai
from typing import List, Dict

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_FINE_TUNED_MODEL")  # ft:…Btd6MRY9

SYSTEM_PROMPT = (
    "You are Wakilni’s support assistant. Analyze user messages "
    "and either reply conversationally or output a JSON "
    "create_issue command for new problems."
)

def build_prompt(conversation: List[Dict], user_input: str) -> List[Dict]:
    """
    Construct the messages list for OpenAI ChatCompletion:
      1. system prompt
      2. entire stored conversation
      3. the new user_input
    """
    msgs = [{"role":"system","content":SYSTEM_PROMPT}]
    for msg in conversation:
        msgs.append({"role": msg["role"], "content": msg["content"]})
    msgs.append({"role":"user","content": user_input})
    return msgs

def call_openai(messages: List[Dict]) -> str:
    """
    Send to OpenAI and return the assistant’s reply.
    """
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

# Alias for compatibility with telegram.py
def build_engineering_prompt(user_input: str, conversation: List[Dict]) -> List[Dict]:
    return build_prompt(conversation, user_input)

