"""Database configuration and models"""
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leonore.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    role = Column(String)
    model = Column(String)
    state = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metrics = Column(JSON, default={})

class Memory(Base):
    __tablename__ = "memory"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    type = Column(String)  # thought, tool_use, reflection, etc
    content = Column(Text)
    embedding = Column(JSON, nullable=True)  # Vector embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=True)
    description = Column(Text)
    status = Column(String)  # pending, running, completed, failed
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default={})

class File(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
