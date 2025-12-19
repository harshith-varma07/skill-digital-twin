"""
Assessment schemas for API validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AssessmentType(str, Enum):
    """Types of assessments."""
    DIAGNOSTIC = "diagnostic"
    SKILL_VALIDATION = "skill_validation"
    PRACTICE = "practice"
    CERTIFICATION = "certification"


class QuestionType(str, Enum):
    """Types of assessment questions."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    CODING = "coding"
    ESSAY = "essay"


class QuestionBase(BaseModel):
    """Base question schema."""
    question_text: str
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    options: Optional[List[str]] = []
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    skill_id: Optional[int] = None
    difficulty_level: float = Field(0.5, ge=0.0, le=1.0)
    points: float = 1.0
    partial_credit: bool = False


class QuestionResponse(QuestionBase):
    """Schema for question response."""
    id: int
    skill_id: Optional[int] = None
    difficulty_level: float
    points: float
    order_index: int
    generated_by_ai: bool
    
    class Config:
        from_attributes = True


class AssessmentBase(BaseModel):
    """Base assessment schema."""
    title: str
    description: Optional[str] = None
    assessment_type: AssessmentType = AssessmentType.DIAGNOSTIC


class AssessmentCreate(AssessmentBase):
    """Schema for creating an assessment."""
    target_skills: Optional[List[int]] = []
    time_limit_minutes: Optional[int] = None
    passing_score: float = 0.7
    max_attempts: int = 3


class AssessmentResponse(AssessmentBase):
    """Schema for assessment response."""
    id: int
    user_id: int
    target_skills: List[int] = []
    time_limit_minutes: Optional[int] = None
    passing_score: float
    max_attempts: int
    score: Optional[float] = None
    completed: bool
    attempts: int
    skill_gaps_identified: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    questions: List[QuestionResponse] = []
    
    class Config:
        from_attributes = True


class AssessmentResponseCreate(BaseModel):
    """Schema for submitting an assessment response."""
    question_id: int
    response_text: Optional[str] = None
    selected_option: Optional[int] = None
    time_spent_seconds: Optional[int] = None


class AssessmentSubmission(BaseModel):
    """Schema for submitting all assessment responses."""
    responses: List[AssessmentResponseCreate]


class DiagnosticRequest(BaseModel):
    """Schema for requesting a diagnostic assessment."""
    skill_areas: Optional[List[str]] = None  # Areas to focus on
    num_questions: int = Field(10, ge=5, le=50)
    difficulty: Optional[str] = "adaptive"  # 'easy', 'medium', 'hard', 'adaptive'
    include_coding: bool = False


class DiagnosticResponse(BaseModel):
    """Schema for diagnostic assessment results."""
    assessment_id: int
    overall_score: float
    skill_breakdown: Dict[str, float]  # skill_name -> score
    identified_gaps: List[Dict[str, Any]]
    strengths: List[Dict[str, Any]]
    recommendations: List[str]
    next_steps: List[str]


class QuestionGenerationRequest(BaseModel):
    """Schema for AI question generation."""
    skill_id: int
    difficulty_level: float = Field(0.5, ge=0.0, le=1.0)
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    num_questions: int = Field(5, ge=1, le=20)
    context: Optional[str] = None
