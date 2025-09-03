from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from contextlib import contextmanager
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_CONFIG = {
    "username": "root",
    "password": "admin", 
    "database": "road_vision_ai",
    "host": "127.0.0.1",
    "dialect": "mysql",
    "port": 3306
}

# Try MySQL first, fallback to SQLite with MySQL schema
try:
    DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}?charset=utf8mb4"
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    # Test connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("✓ Connected to MySQL database")
    DB_TYPE = "mysql"
except Exception as e:
    print(f"⚠ MySQL connection failed: {e}")
    print("📁 Using SQLite with MySQL-compatible schema")
    DATABASE_URL = "sqlite:///./road_vision_ai.db"
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    DB_TYPE = "sqlite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Stream(Base):
    __tablename__ = "streams"
    
    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(String(255), unique=True, index=True, nullable=False)
    source = Column(String(500), nullable=False)
    models = Column(Text, nullable=False)  # JSON string of model names
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StreamResult(Base):
    __tablename__ = "stream_results"
    
    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(String(255), index=True, nullable=False)
    model_name = Column(String(255), nullable=False)
    timestamp = Column(Float, nullable=False)
    result_data = Column(Text, nullable=False)  # JSON string of results
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(String(255), index=True, nullable=False)
    alert_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="medium")
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
