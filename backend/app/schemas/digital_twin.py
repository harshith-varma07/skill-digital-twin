"""
Skill Digital Twin schemas for the complete profile visualization.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SkillNode(BaseModel):
    """Schema for a skill node in the digital twin visualization."""
    id: int
    name: str
    category: Optional[str] = None
    mastery_level: float = Field(0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(0.5, ge=0.0, le=1.0)
    is_gap: bool = False
    gap_severity: Optional[float] = None  # How severe is the gap
    related_skills: List[int] = []
    source: Optional[str] = None
    last_updated: Optional[datetime] = None


class SkillConnection(BaseModel):
    """Schema for connections between skills."""
    source_skill_id: int
    target_skill_id: int
    relationship_type: str  # 'prerequisite', 'related', 'builds_on'
    strength: float = Field(0.5, ge=0.0, le=1.0)


class CategorySummary(BaseModel):
    """Schema for skill category summary."""
    category_id: int
    category_name: str
    total_skills: int
    mastered_skills: int
    average_mastery: float
    skill_ids: List[int] = []


class SkillDigitalTwinResponse(BaseModel):
    """Schema for the complete Skill Digital Twin."""
    user_id: int
    user_name: str
    
    # Skill nodes for visualization
    skill_nodes: List[SkillNode]
    skill_connections: List[SkillConnection]
    
    # Summary statistics
    total_skills: int
    average_mastery: float
    top_skills: List[SkillNode]  # Top 5 strongest skills
    weakest_skills: List[SkillNode]  # Bottom 5 skills
    
    # Category breakdown
    category_summaries: List[CategorySummary]
    
    # Profile metadata
    profile_completeness: float  # 0-100%
    last_assessment_date: Optional[datetime] = None
    total_learning_hours: float = 0.0
    
    # Timestamps
    generated_at: datetime
    data_freshness: str  # 'fresh', 'stale', 'outdated'


class GapAnalysisResponse(BaseModel):
    """Schema for comprehensive gap analysis."""
    user_id: int
    
    # Gap summary
    total_gaps_identified: int
    critical_gaps: List[Dict[str, Any]]  # High priority gaps
    moderate_gaps: List[Dict[str, Any]]
    minor_gaps: List[Dict[str, Any]]
    
    # Gap details
    gaps_by_category: Dict[str, List[Dict[str, Any]]]
    
    # Impact analysis
    career_impact: Dict[str, Any]  # How gaps affect career goals
    learning_priority_order: List[Dict[str, Any]]  # Recommended order to address gaps
    
    # Recommendations
    immediate_actions: List[str]
    short_term_goals: List[Dict[str, Any]]  # 1-3 months
    long_term_goals: List[Dict[str, Any]]  # 3-12 months
    
    # Resources
    recommended_resources: List[Dict[str, Any]]
    estimated_time_to_close_gaps: float  # In hours
    
    # Analysis metadata
    analysis_date: datetime
    confidence_level: float


class ProfileUpdateRequest(BaseModel):
    """Schema for updating the digital twin profile."""
    resume_text: Optional[str] = None
    interests: Optional[List[str]] = None
    academic_background: Optional[Dict[str, Any]] = None
    manual_skills: Optional[List[Dict[str, Any]]] = None  # User-declared skills


class InteractionEvent(BaseModel):
    """Schema for tracking user interactions that update the twin."""
    event_type: str  # 'course_completion', 'assessment', 'resource_viewed', etc.
    skill_ids: List[int]
    score: Optional[float] = None
    duration_seconds: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
