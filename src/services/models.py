
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    platform = Column(String(20), nullable=False)
    phone_number = Column(String(20))
    user_name = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    messages = relationship('Message', back_populates='conversation')

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    message_text = Column(Text)
    message_type = Column(String(20))
    sender = Column(String(20))
    timestamp = Column(DateTime)
    ai_analysis = Column(JSONB)
    jira_ticket_key = Column(String(20))
    language = Column(String(20))
    category = Column(String(50))
    suggestion = Column(Text)
    resolution = Column(Text)
    escalation_flag = Column(Boolean)
    confidence_score = Column(Float)
    conversation = relationship('Conversation', back_populates='messages')

class OnCallSchedule(Base):
    __tablename__ = 'on_call_schedule'
    id = Column(Integer, primary_key=True, index=True)
    engineer_email = Column(String(100), nullable=False)
    engineer_name = Column(String(100), nullable=False)
    jira_username = Column(String(50))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime)

class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    issue_description = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    keywords = Column(ARRAY(Text))
    category = Column(String(50))
    confidence_score = Column(Float, default=1.0)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    source_jira_ticket = Column(String(20))

class IssueOccurrence(Base):
    __tablename__ = 'issue_occurrences'
    id = Column(Integer, primary_key=True, index=True)
    jira_ticket_key = Column(String(20), nullable=False)
    occurrence_count = Column(Integer, default=1)
    first_reported = Column(DateTime)
    last_occurrence = Column(DateTime)
    similar_tickets = Column(ARRAY(Text))
    flagged_for_review = Column(Boolean, default=False)
    issue_signature = Column(Text)

class Config(Base):
    __tablename__ = 'config'
    key = Column(String(50), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime)
