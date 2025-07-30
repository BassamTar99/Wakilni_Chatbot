
# --- Simple In-Memory DB Service for Local Testing ---
# In production, replace with a real database (e.g., PostgreSQL + SQLAlchemy)

from collections import defaultdict
import time

# Store messages as: {user_id: [ {role, text, timestamp}, ... ]}

from datetime import datetime
from typing import List, Dict

_conversations = defaultdict(list)

def save_message(user_id, role, text, timestamp=None):
    """
    Save a message to the conversation history.
    role: 'user', 'assistant', or other valid OpenAI roles
    """
    chat_id = user_id  # Using user_id as chat_id for simplicity
    ts = timestamp or datetime.utcnow()
    _conversations.setdefault(chat_id, []).append({
        "role":    role,
        "content": text,
        "timestamp": ts,
    })

def get_history(user_id, limit=10):
    """
    Retrieve the last N messages for a user (for context-aware prompts).
    """
    return _conversations.get(user_id, []).copy()

def get_conversation(chat_id: str) -> List[Dict]:
    """
    Retrieve the full message list for this chat_id.
    """
    return _conversations.get(chat_id, []).copy()

