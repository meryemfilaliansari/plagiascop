from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.config import Config
import os
Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(100))
    hash = Column(String(64), unique=True)  # SHA-256 hash of content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ComparisonResult(Base):
    __tablename__ = 'comparison_results'
    
    id = Column(Integer, primary_key=True)
    doc_id = Column(Integer, nullable=False)
    compared_doc_id = Column(Integer)
    compared_url = Column(String(500))
    similarity_score = Column(Integer, nullable=False)
    matched_sections = Column(Text)
    detection_method = Column(String(50))
    is_ai_generated = Column(Integer)  # 0: no, 1: yes, 2: uncertain
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialise la base de données et retourne le moteur SQLAlchemy"""
    # Création du répertoire si nécessaire
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{Config.DATABASE_PATH}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()