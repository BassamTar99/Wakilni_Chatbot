
# --- Persistent DB Service using SQLAlchemy ---
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from src.services.db_engine import SessionLocal
from src.services.models import Message, Conversation

def save_message(user_id, role, text, timestamp=None, message_type='text', ai_analysis=None, jira_ticket_key=None):
    """
    Save a message to the conversation history in the database.
    role: 'user', 'assistant', or other valid OpenAI roles
    """
    ts = timestamp or datetime.utcnow()
    db: Session = SessionLocal()
    # Find or create conversation
    conversation = db.query(Conversation).filter_by(user_id=user_id, is_active=True).first()
    if not conversation:
        conversation = Conversation(user_id=user_id, platform='telegram', created_at=ts, updated_at=ts, is_active=True)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    msg = Message(
        conversation_id=conversation.id,
        sender=role,
        message_text=text,
        message_type=message_type,
        timestamp=ts,
        ai_analysis=ai_analysis,
        jira_ticket_key=jira_ticket_key
    )
    db.add(msg)
    conversation.updated_at = ts
    db.commit()
    db.close()

def get_history(user_id, limit=10):
    """
    Retrieve the last N messages for a user from the database.
    """
    db: Session = SessionLocal()
    conversation = db.query(Conversation).filter_by(user_id=user_id, is_active=True).first()
    if not conversation:
        db.close()
        return []
    messages = db.query(Message).filter_by(conversation_id=conversation.id).order_by(Message.timestamp.desc()).limit(limit).all()
    db.close()
    return [
        {
            "role": m.sender,
            "content": m.message_text,
            "timestamp": m.timestamp,
            "ai_analysis": m.ai_analysis,
            "jira_ticket_key": m.jira_ticket_key
        }
        for m in reversed(messages)
    ]

def get_conversation(user_id: str) -> List[Dict]:
    """
    Retrieve the full message list for this user_id from the database.
    """
    db: Session = SessionLocal()
    conversation = db.query(Conversation).filter_by(user_id=user_id, is_active=True).first()
    if not conversation:
        db.close()
        return []
    messages = db.query(Message).filter_by(conversation_id=conversation.id).order_by(Message.timestamp.asc()).all()
    db.close()
    return [
        {
            "role": m.sender,
            "content": m.message_text,
            "timestamp": m.timestamp,
            "ai_analysis": m.ai_analysis,
            "jira_ticket_key": m.jira_ticket_key
        }
        for m in messages
    ]

