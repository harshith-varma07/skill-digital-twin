"""
Skills API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.skill import Skill, SkillCategory, UserSkill
from app.schemas.skill import (
    SkillCreate, SkillResponse, UserSkillCreate, UserSkillResponse,
    SkillCategoryResponse, SkillExtractionRequest, SkillExtractionResponse
)
from app.services.skill_extraction import skill_extraction_service

router = APIRouter()


@router.get("/", response_model=List[SkillResponse])
async def list_skills(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all skills in the ontology."""
    query = select(Skill).options(selectinload(Skill.category))
    
    if category_id:
        query = query.where(Skill.category_id == category_id)
    
    if search:
        query = query.where(Skill.name.ilike(f"%{search}%"))
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new skill in the ontology."""
    # Check if skill exists
    result = await db.execute(select(Skill).where(Skill.name == skill_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already exists"
        )
    
    skill = Skill(
        name=skill_data.name,
        description=skill_data.description,
        category_id=skill_data.category_id,
        keywords=skill_data.keywords or [],
        prerequisites=skill_data.prerequisites or [],
        related_skills=skill_data.related_skills or [],
        domain_weights=skill_data.domain_weights or {}
    )
    
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    
    return skill


@router.get("/categories", response_model=List[SkillCategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List all skill categories."""
    result = await db.execute(select(SkillCategory))
    return result.scalars().all()


@router.get("/user", response_model=List[UserSkillResponse])
async def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's skills."""
    result = await db.execute(
        select(UserSkill)
        .options(selectinload(UserSkill.skill).selectinload(Skill.category))
        .where(UserSkill.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/user", response_model=UserSkillResponse, status_code=status.HTTP_201_CREATED)
async def add_user_skill(
    skill_data: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a skill to user's profile."""
    # Check if skill exists
    result = await db.execute(select(Skill).where(Skill.id == skill_data.skill_id))
    skill = result.scalar_one_or_none()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Check if user already has this skill
    result = await db.execute(
        select(UserSkill)
        .where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill_data.skill_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has this skill"
        )
    
    user_skill = UserSkill(
        user_id=current_user.id,
        skill_id=skill_data.skill_id,
        mastery_level=skill_data.mastery_level,
        source=skill_data.source or "manual",
        evidence=skill_data.evidence or []
    )
    
    db.add(user_skill)
    await db.commit()
    await db.refresh(user_skill)
    
    # Reload with relationships
    result = await db.execute(
        select(UserSkill)
        .options(selectinload(UserSkill.skill))
        .where(UserSkill.id == user_skill.id)
    )
    return result.scalar_one()


@router.put("/user/{skill_id}", response_model=UserSkillResponse)
async def update_user_skill(
    skill_id: int,
    mastery_level: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's skill mastery level."""
    result = await db.execute(
        select(UserSkill)
        .options(selectinload(UserSkill.skill))
        .where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill_id)
    )
    user_skill = result.scalar_one_or_none()
    
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill not found"
        )
    
    user_skill.mastery_level = max(0, min(1, mastery_level))
    await db.commit()
    await db.refresh(user_skill)
    
    return user_skill


@router.delete("/user/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a skill from user's profile."""
    result = await db.execute(
        select(UserSkill)
        .where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill_id)
    )
    user_skill = result.scalar_one_or_none()
    
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User skill not found"
        )
    
    await db.delete(user_skill)
    await db.commit()


@router.post("/extract", response_model=SkillExtractionResponse)
async def extract_skills(
    request: SkillExtractionRequest,
    current_user: User = Depends(get_current_user)
):
    """Extract skills from text using NLP."""
    extracted = await skill_extraction_service.extract_skills(
        text=request.text,
        context=request.context or "general",
        use_ai=True
    )
    
    categorized = skill_extraction_service.categorize_skills(extracted)
    
    confidence_scores = {
        skill["name"]: skill["confidence"]
        for skill in extracted
    }
    
    suggested_categories = {
        skill["name"]: skill["category"]
        for skill in extracted
    }
    
    return SkillExtractionResponse(
        extracted_skills=extracted,
        confidence_scores=confidence_scores,
        suggested_categories=suggested_categories
    )


@router.post("/bulk-add")
async def bulk_add_skills(
    skills: List[UserSkillCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add multiple skills at once."""
    added = []
    skipped = []
    
    for skill_data in skills:
        # Check if user already has this skill
        result = await db.execute(
            select(UserSkill)
            .where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill_data.skill_id)
        )
        
        if result.scalar_one_or_none():
            skipped.append(skill_data.skill_id)
            continue
        
        user_skill = UserSkill(
            user_id=current_user.id,
            skill_id=skill_data.skill_id,
            mastery_level=skill_data.mastery_level,
            source=skill_data.source or "bulk_add",
            evidence=skill_data.evidence or []
        )
        db.add(user_skill)
        added.append(skill_data.skill_id)
    
    await db.commit()
    
    return {
        "added": added,
        "skipped": skipped,
        "total_added": len(added)
    }
