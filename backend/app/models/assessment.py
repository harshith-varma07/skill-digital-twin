"""
Assessment models for diagnostic testing and skill evaluation.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, JSON, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class AssessmentType(enum.Enum):
    """Types of assessments."""
    DIAGNOSTIC = "diagnostic"
    SKILL_VALIDATION = "skill_validation"
    PRACTICE = "practice"
    CERTIFICATION = "certification"


class QuestionType(enum.Enum):
    """Types of assessment questions."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    CODING = "coding"
    ESSAY = "essay"


class Assessment(Base):
    """Assessment/quiz model for skill evaluation."""
    
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assessment_type = Column(Enum(AssessmentType), default=AssessmentType.DIAGNOSTIC)
    
    # Skills being assessed
    target_skills = Column(JSON, default=list)  # List of skill IDs
    
    # Assessment configuration
    time_limit_minutes = Column(Integer, nullable=True)
    passing_score = Column(Float, default=0.7)
    max_attempts = Column(Integer, default=3)
    
    # Results
    score = Column(Float, nullable=True)
    completed = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    
    # AI-generated insights
    skill_gaps_identified = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    responses = relationship("AssessmentResponse", back_populates="assessment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment {self.title}>"


class AssessmentQuestion(Base):
    """Individual question in an assessment."""
    
    __tablename__ = "assessment_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.MULTIPLE_CHOICE)
    
    # Question content
    options = Column(JSON, default=list)  # For multiple choice
    correct_answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    
    # Skill mapping
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    difficulty_level = Column(Float, default=0.5)  # 0.0 to 1.0
    
    # Scoring
    points = Column(Float, default=1.0)
    partial_credit = Column(Boolean, default=False)
    
    # Order in assessment
    order_index = Column(Integer, default=0)
    
    # AI generation metadata
    generated_by_ai = Column(Boolean, default=True)
    generation_prompt = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    responses = relationship("AssessmentResponse", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AssessmentQuestion {self.id}>"


class AssessmentResponse(Base):
    """User's response to an assessment question."""
    
    __tablename__ = "assessment_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("assessment_questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Response content
    response_text = Column(Text, nullable=True)
    selected_option = Column(Integer, nullable=True)  # Index of selected option
    
    # Evaluation
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, default=0.0)
    
    # AI evaluation for open-ended questions
    ai_feedback = Column(Text, nullable=True)
    ai_score = Column(Float, nullable=True)
    
    # Time tracking
    time_spent_seconds = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    question = relationship("AssessmentQuestion", back_populates="responses")
    
    def __repr__(self):
        return f"<AssessmentResponse assessment={self.assessment_id} question={self.question_id}>"
