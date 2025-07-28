
# --- Simple In-Memory DB Service for Local Testing ---
# In production, replace with a real database (e.g., PostgreSQL + SQLAlchemy)

from collections import defaultdict
import time

# Store messages as: {user_id: [ {role, text, timestamp}, ... ]}
_conversations = defaultdict(list)

def save_message(user_id, role, text, timestamp=None):
    """
    Save a message to the conversation history.
    role: 'user' or 'bot'
    """
    if timestamp is None:
        timestamp = int(time.time())
    _conversations[user_id].append({
        "role": role,
        "text": text,
        "timestamp": timestamp
    })

def get_history(user_id, limit=10):
    """
    Retrieve the last N messages for a user (for context-aware prompts).
    """
    return _conversations[user_id][-limit:]

