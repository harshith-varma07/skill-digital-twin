"""
Career API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.career import CareerRole, CareerSkillRequirement, CareerAlignment
from app.schemas.career import (
    CareerRoleCreate, CareerRoleResponse, CareerAlignmentResponse,
    CareerAnalysisRequest, CareerAnalysisResponse
)
from app.services.career_service import career_service

router = APIRouter()


@router.get("/roles", response_model=List[CareerRoleResponse])
async def list_career_roles(
    industry: Optional[str] = None,
    experience_level: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List available career roles."""
    query = select(CareerRole).options(
        selectinload(CareerRole.skill_requirements).selectinload(CareerSkillRequirement.skill)
    )
    
    if industry:
        query = query.where(CareerRole.industry == industry)
    
    if experience_level:
        from app.models.career import ExperienceLevel
        try:
            level = ExperienceLevel(experience_level)
            query = query.where(CareerRole.experience_level == level)
        except ValueError:
            pass
    
    if search:
        query = query.where(CareerRole.title.ilike(f"%{search}%"))
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    roles = result.scalars().all()
    
    # Format response with skill requirements
    formatted_roles = []
    for role in roles:
        role_dict = {
            "id": role.id,
            "title": role.title,
            "description": role.description,
            "industry": role.industry,
            "domain": role.domain,
            "experience_level": role.experience_level,
            "salary_min": role.salary_min,
            "salary_max": role.salary_max,
            "salary_currency": role.salary_currency,
            "demand_score": role.demand_score,
            "growth_rate": role.growth_rate,
            "responsibilities": role.responsibilities,
            "typical_companies": role.typical_companies,
            "skill_requirements": [
                {
                    "skill_id": req.skill_id,
                    "skill_name": req.skill.name if req.skill else "Unknown",
                    "required_level": req.required_level,
                    "importance": req.importance,
                    "is_mandatory": req.is_mandatory,
                    "category": req.category
                }
                for req in role.skill_requirements
            ],
            "created_at": role.created_at,
            "updated_at": role.updated_at
        }
        formatted_roles.append(role_dict)
    
    return formatted_roles


@router.get("/roles/{role_id}")
async def get_career_role(
    role_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get career role details."""
    result = await db.execute(
        select(CareerRole)
        .options(selectinload(CareerRole.skill_requirements).selectinload(CareerSkillRequirement.skill))
        .where(CareerRole.id == role_id)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career role not found"
        )
    
    return {
        "id": role.id,
        "title": role.title,
        "description": role.description,
        "industry": role.industry,
        "domain": role.domain,
        "experience_level": role.experience_level.value if role.experience_level else None,
        "salary_min": role.salary_min,
        "salary_max": role.salary_max,
        "salary_currency": role.salary_currency,
        "demand_score": role.demand_score,
        "growth_rate": role.growth_rate,
        "responsibilities": role.responsibilities,
        "typical_companies": role.typical_companies,
        "skill_requirements": [
            {
                "skill_id": req.skill_id,
                "skill_name": req.skill.name if req.skill else "Unknown",
                "required_level": req.required_level,
                "importance": req.importance,
                "is_mandatory": req.is_mandatory,
                "category": req.category
            }
            for req in role.skill_requirements
        ]
    }


@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_career_role(
    role_data: CareerRoleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new career role."""
    from app.models.career import ExperienceLevel
    
    role = CareerRole(
        title=role_data.title,
        description=role_data.description,
        industry=role_data.industry,
        domain=role_data.domain,
        experience_level=role_data.experience_level,
        salary_min=role_data.salary_min,
        salary_max=role_data.salary_max,
        salary_currency=role_data.salary_currency,
        responsibilities=role_data.responsibilities or [],
        typical_companies=role_data.typical_companies or []
    )
    
    db.add(role)
    await db.commit()
    await db.refresh(role)
    
    return {"id": role.id, "title": role.title, "message": "Career role created"}


@router.get("/alignment/{role_id}")
async def get_career_alignment(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get alignment analysis for a specific career role."""
    alignment = await career_service.calculate_career_alignment(
        db=db,
        user_id=current_user.id,
        career_role_id=role_id
    )
    
    if not alignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career role not found"
        )
    
    # Get role details
    result = await db.execute(select(CareerRole).where(CareerRole.id == role_id))
    role = result.scalar_one_or_none()
    
    alignment["career_role"] = {
        "id": role.id,
        "title": role.title,
        "description": role.description
    } if role else None
    
    # Convert to percentage
    alignment["overall_readiness_percentage"] = round(alignment["overall_readiness"] * 100, 1)
    
    return alignment


@router.post("/analyze")
async def analyze_career_options(
    request: CareerAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze career alignment across multiple roles."""
    recommendations = await career_service.get_career_recommendations(
        db=db,
        user_id=current_user.id,
        min_readiness=request.min_readiness_threshold
    )
    
    return {
        "user_id": current_user.id,
        "ready_careers": [
            {
                **career,
                "readiness_percentage": round(career["overall_readiness"] * 100, 1)
            }
            for career in recommendations["ready_careers"]
        ],
        "stretch_careers": [
            {
                **career,
                "readiness_percentage": round(career["overall_readiness"] * 100, 1)
            }
            for career in recommendations["stretch_careers"]
        ],
        "priority_skills_to_develop": recommendations["priority_skills_to_develop"],
        "analysis_timestamp": recommendations["analysis_timestamp"]
    }


@router.get("/recommendations")
async def get_career_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized career recommendations."""
    recommendations = await career_service.get_career_recommendations(
        db=db,
        user_id=current_user.id,
        min_readiness=0.3
    )
    
    return {
        "top_matches": [
            {
                "career_title": career.get("career_role_title", "Unknown"),
                "readiness_percentage": round(career["overall_readiness"] * 100, 1),
                "skill_gaps_count": len(career["skill_gaps"]),
                "strengths_count": len(career["strengths"]),
                "estimated_time_to_ready_hours": career["estimated_time_to_ready"]
            }
            for career in recommendations["ready_careers"][:5]
        ],
        "skills_to_focus": recommendations["priority_skills_to_develop"],
        "stretch_opportunities": [
            {
                "career_title": career.get("career_role_title", "Unknown"),
                "readiness_percentage": round(career["overall_readiness"] * 100, 1)
            }
            for career in recommendations["stretch_careers"][:3]
        ]
    }


@router.post("/roles/{role_id}/set-target")
async def set_target_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set a career role as the user's target."""
    # Check if role exists
    result = await db.execute(select(CareerRole).where(CareerRole.id == role_id))
    role = result.scalar_one_or_none()
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Career role not found"
        )
    
    # Check for existing alignment
    result = await db.execute(
        select(CareerAlignment)
        .where(CareerAlignment.user_id == current_user.id, CareerAlignment.career_role_id == role_id)
    )
    alignment = result.scalar_one_or_none()
    
    if alignment:
        alignment.is_target_role = True
    else:
        # Calculate and create alignment
        alignment_data = await career_service.calculate_career_alignment(
            db=db,
            user_id=current_user.id,
            career_role_id=role_id
        )
        
        alignment = CareerAlignment(
            user_id=current_user.id,
            career_role_id=role_id,
            overall_readiness=alignment_data["overall_readiness"],
            skill_match_score=alignment_data["skill_match_score"],
            experience_match_score=alignment_data["experience_match_score"],
            skill_gaps=alignment_data["skill_gaps"],
            strengths=alignment_data["strengths"],
            upskilling_recommendations=alignment_data["upskilling_recommendations"],
            estimated_time_to_ready=alignment_data["estimated_time_to_ready"],
            priority_skills=alignment_data["priority_skills"],
            is_target_role=True
        )
        db.add(alignment)
    
    # Unset other target roles
    other_targets = await db.execute(
        select(CareerAlignment)
        .where(
            CareerAlignment.user_id == current_user.id,
            CareerAlignment.career_role_id != role_id,
            CareerAlignment.is_target_role == True
        )
    )
    for other in other_targets.scalars().all():
        other.is_target_role = False
    
    await db.commit()
    
    return {"message": f"Set {role.title} as target career", "role_id": role_id}
