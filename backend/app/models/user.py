"""
User model for the Skill Digital Twin system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """User model representing learners in the system."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Profile information
    bio = Column(Text, nullable=True)
    education_level = Column(String(100), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    years_of_experience = Column(Integer, default=0)
    interests = Column(JSON, default=list)  # List of interests
    
    # Resume and academic data
    resume_text = Column(Text, nullable=True)
    academic_background = Column(JSON, default=dict)
    
    # Settings
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")
    learning_roadmaps = relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan")
    career_alignments = relationship("CareerAlignment", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
