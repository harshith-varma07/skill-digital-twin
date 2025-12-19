"""
Career role and alignment models.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ExperienceLevel(enum.Enum):
    """Experience level for career roles."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


class CareerRole(Base):
    """Career role/job profile in the system."""
    
    __tablename__ = "career_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Role details
    industry = Column(String(100), nullable=True)
    domain = Column(String(100), nullable=True)
    experience_level = Column(Enum(ExperienceLevel), default=ExperienceLevel.MID)
    
    # Salary information
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="USD")
    
    # Job market data
    demand_score = Column(Float, default=0.5)  # Market demand
    growth_rate = Column(Float, default=0.0)  # Expected growth
    
    # Additional info
    responsibilities = Column(JSON, default=list)
    typical_companies = Column(JSON, default=list)
    
    # Embedding for matching
    embedding = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    skill_requirements = relationship("CareerSkillRequirement", back_populates="career_role", cascade="all, delete-orphan")
    alignments = relationship("CareerAlignment", back_populates="career_role")
    
    def __repr__(self):
        return f"<CareerRole {self.title}>"


class CareerSkillRequirement(Base):
    """Skill requirement for a career role."""
    
    __tablename__ = "career_skill_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    career_role_id = Column(Integer, ForeignKey("career_roles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    
    # Requirement details
    required_level = Column(Float, default=0.5)  # 0.0 to 1.0
    importance = Column(Float, default=0.5)  # How important is this skill
    is_mandatory = Column(Boolean, default=False)
    
    # Category
    category = Column(String(50), default="technical")  # 'technical', 'soft', 'domain'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    career_role = relationship("CareerRole", back_populates="skill_requirements")
    skill = relationship("Skill", back_populates="career_requirements")
    
    def __repr__(self):
        return f"<CareerSkillRequirement role={self.career_role_id} skill={self.skill_id}>"


from sqlalchemy import Boolean


class CareerAlignment(Base):
    """User's alignment with a career role."""
    
    __tablename__ = "career_alignments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_role_id = Column(Integer, ForeignKey("career_roles.id"), nullable=False)
    
    # Alignment scores
    overall_readiness = Column(Float, default=0.0)  # 0.0 to 1.0 (100%)
    skill_match_score = Column(Float, default=0.0)
    experience_match_score = Column(Float, default=0.0)
    
    # Detailed breakdown
    skill_gaps = Column(JSON, default=list)  # List of {skill_id, current_level, required_level, gap}
    strengths = Column(JSON, default=list)  # Skills that exceed requirements
    
    # Recommendations
    upskilling_recommendations = Column(JSON, default=list)
    estimated_time_to_ready = Column(Float, nullable=True)  # In hours
    priority_skills = Column(JSON, default=list)  # Skills to focus on first
    
    # User preference
    is_target_role = Column(Boolean, default=False)
    interest_level = Column(Float, default=0.5)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="career_alignments")
    career_role = relationship("CareerRole", back_populates="alignments")
    
    def __repr__(self):
        return f"<CareerAlignment user={self.user_id} role={self.career_role_id} readiness={self.overall_readiness}>"
