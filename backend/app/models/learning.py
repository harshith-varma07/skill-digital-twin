"""
Learning roadmap and resource models.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ModuleStatus(enum.Enum):
    """Status of learning module."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ResourceType(enum.Enum):
    """Types of learning resources."""
    VIDEO = "video"
    ARTICLE = "article"
    COURSE = "course"
    BOOK = "book"
    TUTORIAL = "tutorial"
    PRACTICE = "practice"
    PROJECT = "project"


class LearningRoadmap(Base):
    """Personalized learning roadmap for a user."""
    
    __tablename__ = "learning_roadmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Target skills and goals
    target_skills = Column(JSON, default=list)  # List of skill IDs to develop
    target_career_role = Column(String(255), nullable=True)
    
    # Progress tracking
    overall_progress = Column(Float, default=0.0)  # 0.0 to 1.0
    estimated_hours = Column(Float, nullable=True)
    hours_completed = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    completed = Column(Boolean, default=False)
    
    # AI generation metadata
    generated_by_ai = Column(Boolean, default=True)
    generation_context = Column(JSON, default=dict)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_roadmaps")
    modules = relationship("LearningModule", back_populates="roadmap", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningRoadmap {self.title}>"


class LearningModule(Base):
    """A module/section within a learning roadmap."""
    
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("learning_roadmaps.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Topic overview (AI-generated)
    topic_overview = Column(Text, nullable=True)
    key_concepts = Column(JSON, default=list)
    learning_objectives = Column(JSON, default=list)
    
    # Skills addressed
    target_skill_ids = Column(JSON, default=list)
    
    # Progress
    status = Column(Enum(ModuleStatus), default=ModuleStatus.NOT_STARTED)
    progress = Column(Float, default=0.0)
    estimated_hours = Column(Float, nullable=True)
    
    # Order in roadmap
    order_index = Column(Integer, default=0)
    
    # Prerequisites (other module IDs)
    prerequisites = Column(JSON, default=list)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmap = relationship("LearningRoadmap", back_populates="modules")
    resources = relationship("LearningResource", back_populates="module", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningModule {self.title}>"


class LearningResource(Base):
    """A learning resource within a module."""
    
    __tablename__ = "learning_resources"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(Enum(ResourceType), default=ResourceType.VIDEO)
    
    # Resource details
    url = Column(String(500), nullable=True)
    platform = Column(String(100), nullable=True)  # 'youtube', 'coursera', etc.
    
    # YouTube specific
    youtube_video_id = Column(String(50), nullable=True)
    youtube_channel = Column(String(255), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    
    # Quality indicators
    relevance_score = Column(Float, default=0.0)  # How relevant to the skill
    quality_score = Column(Float, default=0.0)  # Overall quality rating
    view_count = Column(Integer, nullable=True)
    like_count = Column(Integer, nullable=True)
    
    # User progress
    completed = Column(Boolean, default=False)
    watch_progress = Column(Float, default=0.0)  # For videos
    notes = Column(Text, nullable=True)  # User notes
    
    # Order in module
    order_index = Column(Integer, default=0)
    
    # AI recommendation metadata
    ai_recommended = Column(Boolean, default=True)
    recommendation_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    module = relationship("LearningModule", back_populates="resources")
    
    def __repr__(self):
        return f"<LearningResource {self.title}>"
