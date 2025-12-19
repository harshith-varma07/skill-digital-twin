"""
Assessment API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.assessment import Assessment, AssessmentQuestion
from app.schemas.assessment import (
    AssessmentCreate, AssessmentResponse, DiagnosticRequest,
    DiagnosticResponse, AssessmentSubmission, QuestionGenerationRequest
)
from app.services.assessment_service import assessment_service

router = APIRouter()


@router.get("/", response_model=List[AssessmentResponse])
async def list_assessments(
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's assessments."""
    query = select(Assessment).options(
        selectinload(Assessment.questions)
    ).where(Assessment.user_id == current_user.id)
    
    if completed is not None:
        query = query.where(Assessment.completed == completed)
    
    query = query.order_by(Assessment.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get assessment details."""
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.questions))
        .where(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    return assessment


@router.post("/diagnostic", response_model=AssessmentResponse)
async def create_diagnostic_assessment(
    request: DiagnosticRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a diagnostic assessment."""
    assessment = await assessment_service.create_diagnostic_assessment(
        db=db,
        user_id=current_user.id,
        skill_areas=request.skill_areas,
        num_questions=request.num_questions,
        difficulty=request.difficulty
    )
    
    # Reload with questions
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.questions))
        .where(Assessment.id == assessment.id)
    )
    
    return result.scalar_one()


@router.post("/{assessment_id}/start")
async def start_assessment(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start an assessment."""
    result = await db.execute(
        select(Assessment)
        .where(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if assessment.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment already completed"
        )
    
    if assessment.attempts >= assessment.max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum attempts reached"
        )
    
    from datetime import datetime
    assessment.started_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Assessment started", "started_at": assessment.started_at}


@router.post("/{assessment_id}/submit")
async def submit_assessment(
    assessment_id: int,
    submission: AssessmentSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit assessment responses."""
    # Submit each response
    for response_data in submission.responses:
        await assessment_service.submit_response(
            db=db,
            assessment_id=assessment_id,
            question_id=response_data.question_id,
            user_id=current_user.id,
            response_text=response_data.response_text,
            selected_option=response_data.selected_option,
            time_spent_seconds=response_data.time_spent_seconds
        )
    
    # Complete assessment
    results = await assessment_service.complete_assessment(
        db=db,
        assessment_id=assessment_id,
        user_id=current_user.id
    )
    
    return results


@router.get("/{assessment_id}/results")
async def get_assessment_results(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get assessment results."""
    result = await db.execute(
        select(Assessment)
        .options(
            selectinload(Assessment.questions),
            selectinload(Assessment.responses)
        )
        .where(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    if not assessment.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assessment not completed yet"
        )
    
    return {
        "assessment_id": assessment.id,
        "title": assessment.title,
        "score": assessment.score,
        "passed": assessment.score >= assessment.passing_score if assessment.score else False,
        "skill_gaps_identified": assessment.skill_gaps_identified,
        "recommendations": assessment.recommendations,
        "completed_at": assessment.completed_at
    }


@router.post("/practice-questions")
async def generate_practice_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate practice questions for a skill."""
    questions = await assessment_service.generate_practice_questions(
        db=db,
        skill_id=request.skill_id,
        num_questions=request.num_questions,
        difficulty=request.difficulty_level
    )
    
    return {
        "skill_id": request.skill_id,
        "questions": questions,
        "count": len(questions)
    }
