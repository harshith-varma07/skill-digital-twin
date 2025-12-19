"""
Career alignment schemas for API validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level for career roles."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


class CareerRoleBase(BaseModel):
    """Base career role schema."""
    title: str
    description: Optional[str] = None
    industry: Optional[str] = None
    domain: Optional[str] = None


class CareerRoleCreate(CareerRoleBase):
    """Schema for creating a career role."""
    experience_level: ExperienceLevel = ExperienceLevel.MID
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    responsibilities: Optional[List[str]] = []
    typical_companies: Optional[List[str]] = []


class SkillRequirementResponse(BaseModel):
    """Schema for skill requirement in a career role."""
    skill_id: int
    skill_name: str
    required_level: float
    importance: float
    is_mandatory: bool
    category: str
    
    class Config:
        from_attributes = True


class CareerRoleResponse(CareerRoleBase):
    """Schema for career role response."""
    id: int
    experience_level: ExperienceLevel
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str
    demand_score: float
    growth_rate: float
    responsibilities: List[str] = []
    typical_companies: List[str] = []
    skill_requirements: List[SkillRequirementResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SkillGapDetail(BaseModel):
    """Schema for detailed skill gap information."""
    skill_id: int
    skill_name: str
    current_level: float
    required_level: float
    gap: float
    importance: float
    is_mandatory: bool
    recommended_resources: List[Dict[str, Any]] = []


class CareerAlignmentResponse(BaseModel):
    """Schema for career alignment response."""
    id: int
    user_id: int
    career_role_id: int
    career_role: CareerRoleResponse
    overall_readiness: float  # Percentage (0-100)
    skill_match_score: float
    experience_match_score: float
    skill_gaps: List[SkillGapDetail] = []
    strengths: List[Dict[str, Any]] = []
    upskilling_recommendations: List[Dict[str, Any]] = []
    estimated_time_to_ready: Optional[float] = None  # In hours
    priority_skills: List[Dict[str, Any]] = []
    is_target_role: bool
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class CareerAnalysisRequest(BaseModel):
    """Schema for requesting career analysis."""
    target_roles: Optional[List[int]] = None  # Specific role IDs
    industries: Optional[List[str]] = None
    experience_levels: Optional[List[ExperienceLevel]] = None
    min_readiness_threshold: float = Field(0.0, ge=0.0, le=1.0)
    include_recommendations: bool = True


class CareerRecommendation(BaseModel):
    """Schema for a career recommendation."""
    career_role: CareerRoleResponse
    readiness_percentage: float
    match_score: float
    key_gaps: List[str]
    key_strengths: List[str]
    time_to_ready_hours: Optional[float] = None
    action_items: List[str]


class CareerAnalysisResponse(BaseModel):
    """Schema for career analysis response."""
    user_id: int
    total_roles_analyzed: int
    top_matches: List[CareerRecommendation]
    skill_summary: Dict[str, float]  # Overall skill levels by category
    market_insights: Dict[str, Any]
    recommended_focus_areas: List[str]
    analysis_timestamp: datetime
