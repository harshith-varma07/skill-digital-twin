"""
Skill schemas for API validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SkillLevel(str, Enum):
    """Skill mastery levels."""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class SkillCategoryBase(BaseModel):
    """Base skill category schema."""
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class SkillCategoryCreate(SkillCategoryBase):
    """Schema for creating a skill category."""
    pass


class SkillCategoryResponse(SkillCategoryBase):
    """Schema for skill category response."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SkillBase(BaseModel):
    """Base skill schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None


class SkillCreate(SkillBase):
    """Schema for creating a skill."""
    keywords: Optional[List[str]] = []
    prerequisites: Optional[List[int]] = []
    related_skills: Optional[List[int]] = []
    domain_weights: Optional[Dict[str, float]] = {}


class SkillResponse(SkillBase):
    """Schema for skill response."""
    id: int
    keywords: List[str] = []
    prerequisites: List[int] = []
    related_skills: List[int] = []
    domain_weights: Dict[str, float] = {}
    created_at: datetime
    updated_at: datetime
    category: Optional[SkillCategoryResponse] = None
    
    class Config:
        from_attributes = True


class UserSkillBase(BaseModel):
    """Base user skill schema."""
    skill_id: int
    mastery_level: float = Field(0.0, ge=0.0, le=1.0)


class UserSkillCreate(UserSkillBase):
    """Schema for creating a user skill."""
    source: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = []


class UserSkillUpdate(BaseModel):
    """Schema for updating a user skill."""
    mastery_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    source: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None


class UserSkillResponse(UserSkillBase):
    """Schema for user skill response."""
    id: int
    user_id: int
    skill_level: SkillLevel
    confidence_score: float
    source: Optional[str] = None
    evidence: List[Dict[str, Any]] = []
    last_assessed: Optional[datetime] = None
    improvement_rate: float = 0.0
    created_at: datetime
    updated_at: datetime
    skill: Optional[SkillResponse] = None
    
    class Config:
        from_attributes = True


class SkillExtractionRequest(BaseModel):
    """Schema for skill extraction from text."""
    text: str = Field(..., min_length=10)
    context: Optional[str] = None  # 'resume', 'academic', 'self_description'


class SkillExtractionResponse(BaseModel):
    """Schema for skill extraction response."""
    extracted_skills: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    suggested_categories: Dict[str, str]
