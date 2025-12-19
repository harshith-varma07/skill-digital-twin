"""
Learning roadmap schemas for API validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ModuleStatus(str, Enum):
    """Status of learning module."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ResourceType(str, Enum):
    """Types of learning resources."""
    VIDEO = "video"
    ARTICLE = "article"
    COURSE = "course"
    BOOK = "book"
    TUTORIAL = "tutorial"
    PRACTICE = "practice"
    PROJECT = "project"


class LearningResourceBase(BaseModel):
    """Base learning resource schema."""
    title: str
    description: Optional[str] = None
    resource_type: ResourceType = ResourceType.VIDEO
    url: Optional[str] = None


class LearningResourceCreate(LearningResourceBase):
    """Schema for creating a learning resource."""
    platform: Optional[str] = None
    youtube_video_id: Optional[str] = None
    duration_seconds: Optional[int] = None


class LearningResourceResponse(LearningResourceBase):
    """Schema for learning resource response."""
    id: int
    platform: Optional[str] = None
    youtube_video_id: Optional[str] = None
    youtube_channel: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
    relevance_score: float
    quality_score: float
    view_count: Optional[int] = None
    completed: bool
    watch_progress: float
    order_index: int
    recommendation_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class LearningModuleBase(BaseModel):
    """Base learning module schema."""
    title: str
    description: Optional[str] = None


class LearningModuleCreate(LearningModuleBase):
    """Schema for creating a learning module."""
    topic_overview: Optional[str] = None
    key_concepts: Optional[List[str]] = []
    learning_objectives: Optional[List[str]] = []
    target_skill_ids: Optional[List[int]] = []
    estimated_hours: Optional[float] = None


class LearningModuleResponse(LearningModuleBase):
    """Schema for learning module response."""
    id: int
    topic_overview: Optional[str] = None
    key_concepts: List[str] = []
    learning_objectives: List[str] = []
    target_skill_ids: List[int] = []
    status: ModuleStatus
    progress: float
    estimated_hours: Optional[float] = None
    order_index: int
    prerequisites: List[int] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resources: List[LearningResourceResponse] = []
    
    class Config:
        from_attributes = True


class LearningRoadmapBase(BaseModel):
    """Base learning roadmap schema."""
    title: str
    description: Optional[str] = None


class LearningRoadmapCreate(LearningRoadmapBase):
    """Schema for creating a learning roadmap."""
    target_skills: Optional[List[int]] = []
    target_career_role: Optional[str] = None


class LearningRoadmapResponse(LearningRoadmapBase):
    """Schema for learning roadmap response."""
    id: int
    user_id: int
    target_skills: List[int] = []
    target_career_role: Optional[str] = None
    overall_progress: float
    estimated_hours: Optional[float] = None
    hours_completed: float
    is_active: bool
    completed: bool
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    modules: List[LearningModuleResponse] = []
    
    class Config:
        from_attributes = True


class RoadmapGenerationRequest(BaseModel):
    """Schema for requesting AI-generated roadmap."""
    target_skills: Optional[List[int]] = None
    target_career_role: Optional[str] = None
    skill_gaps: Optional[List[Dict[str, Any]]] = None
    current_level: Optional[str] = "beginner"
    available_hours_per_week: Optional[int] = 10
    preferred_learning_style: Optional[str] = "video"  # 'video', 'reading', 'hands_on', 'mixed'
    include_practice_questions: bool = True


class RoadmapProgressUpdate(BaseModel):
    """Schema for updating roadmap progress."""
    module_id: Optional[int] = None
    resource_id: Optional[int] = None
    status: Optional[ModuleStatus] = None
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    completed: Optional[bool] = None


class YouTubeRecommendationRequest(BaseModel):
    """Schema for YouTube video recommendations."""
    topic: str
    skill_level: Optional[str] = "beginner"
    max_results: int = Field(10, ge=1, le=50)
    duration_preference: Optional[str] = "medium"  # 'short', 'medium', 'long'


class YouTubeVideoResponse(BaseModel):
    """Schema for YouTube video details."""
    video_id: str
    title: str
    description: str
    channel_title: str
    thumbnail_url: str
    duration_seconds: int
    view_count: int
    like_count: Optional[int] = None
    relevance_score: float
    url: str
