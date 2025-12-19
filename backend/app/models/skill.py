"""
Skill models for the Skill Digital Twin system.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class SkillLevel(enum.Enum):
    """Skill mastery levels."""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategory(Base):
    """Skill category for organizing skills in ontology."""
    
    __tablename__ = "skill_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("skill_categories.id"), nullable=True)
    
    # Hierarchical relationship
    parent = relationship("SkillCategory", remote_side=[id], backref="subcategories")
    skills = relationship("Skill", back_populates="category")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SkillCategory {self.name}>"


class Skill(Base):
    """Skill model representing individual skills in the ontology."""
    
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("skill_categories.id"), nullable=True)
    
    # Skill metadata
    keywords = Column(JSON, default=list)  # Related keywords for NLP matching
    prerequisites = Column(JSON, default=list)  # List of prerequisite skill IDs
    related_skills = Column(JSON, default=list)  # Related skill IDs
    
    # Embedding for semantic matching
    embedding = Column(JSON, nullable=True)  # Stored as list of floats
    
    # Importance weights for different domains
    domain_weights = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("SkillCategory", back_populates="skills")
    user_skills = relationship("UserSkill", back_populates="skill")
    career_requirements = relationship("CareerSkillRequirement", back_populates="skill")
    
    def __repr__(self):
        return f"<Skill {self.name}>"


class UserSkill(Base):
    """User's skill proficiency mapping."""
    
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    # Mastery tracking
    mastery_level = Column(Float, default=0.0)  # 0.0 to 1.0
    skill_level = Column(Enum(SkillLevel), default=SkillLevel.NOVICE)
    confidence_score = Column(Float, default=0.5)  # How confident we are in the assessment
    
    # Source tracking
    source = Column(String(50), nullable=True)  # 'resume', 'assessment', 'course', 'manual'
    evidence = Column(JSON, default=list)  # List of evidence supporting the skill level
    
    # Progress tracking
    last_assessed = Column(DateTime, nullable=True)
    improvement_rate = Column(Float, default=0.0)  # Rate of improvement
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")
    
    def __repr__(self):
        return f"<UserSkill user={self.user_id} skill={self.skill_id} level={self.mastery_level}>"
