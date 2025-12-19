"""
Digital Twin API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.digital_twin import (
    SkillDigitalTwinResponse, GapAnalysisResponse,
    ProfileUpdateRequest, InteractionEvent
)
from app.services.digital_twin_service import digital_twin_service

router = APIRouter()


@router.get("/profile", response_model=SkillDigitalTwinResponse)
async def get_digital_twin_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the complete Skill Digital Twin profile for visualization."""
    twin = await digital_twin_service.generate_digital_twin(
        db=db,
        user_id=current_user.id
    )
    
    if not twin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not generate digital twin"
        )
    
    return twin


@router.get("/gap-analysis")
async def get_gap_analysis(
    target_role_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive gap analysis."""
    analysis = await digital_twin_service.perform_gap_analysis(
        db=db,
        user_id=current_user.id,
        target_role_id=target_role_id
    )
    
    return analysis


@router.post("/gap-analysis/skills")
async def get_gap_analysis_for_skills(
    target_skills: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get gap analysis for specific target skills."""
    analysis = await digital_twin_service.perform_gap_analysis(
        db=db,
        user_id=current_user.id,
        target_skills=target_skills
    )
    
    return analysis


@router.post("/update")
async def update_profile_data(
    update_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update digital twin profile with new data."""
    from app.services.skill_extraction import skill_extraction_service
    from app.models.skill import Skill, UserSkill
    from sqlalchemy import select
    
    updates_made = []
    
    # Update resume
    if update_data.resume_text:
        current_user.resume_text = update_data.resume_text
        
        # Extract skills
        extracted = await skill_extraction_service.extract_skills(
            text=update_data.resume_text,
            context="resume"
        )
        
        # Add new skills
        for skill_data in extracted:
            skill_name = skill_data["name"]
            result = await db.execute(
                select(Skill).where(Skill.name.ilike(skill_name))
            )
            skill = result.scalar_one_or_none()
            
            if skill:
                # Check if user has this skill
                result = await db.execute(
                    select(UserSkill)
                    .where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill.id)
                )
                user_skill = result.scalar_one_or_none()
                
                if not user_skill:
                    proficiency_map = {
                        "beginner": 0.3,
                        "intermediate": 0.5,
                        "advanced": 0.7,
                        "expert": 0.9
                    }
                    mastery = proficiency_map.get(skill_data.get("proficiency_hint", "intermediate"), 0.5)
                    
                    user_skill = UserSkill(
                        user_id=current_user.id,
                        skill_id=skill.id,
                        mastery_level=mastery,
                        confidence_score=skill_data.get("confidence", 0.6),
                        source="resume"
                    )
                    db.add(user_skill)
                    updates_made.append(f"Added skill: {skill_name}")
    
    # Update interests
    if update_data.interests:
        current_user.interests = update_data.interests
        updates_made.append("Updated interests")
    
    # Update academic background
    if update_data.academic_background:
        current_user.academic_background = update_data.academic_background
        updates_made.append("Updated academic background")
    
    # Add manual skills
    if update_data.manual_skills:
        for skill_info in update_data.manual_skills:
            skill_id = skill_info.get("skill_id")
            mastery = skill_info.get("mastery_level", 0.5)
            
            if skill_id:
                result = await db.execute(
                    select(UserSkill)
                    .where(UserSkill.user_id == current_user.id, UserSkill.skill_id == skill_id)
                )
                user_skill = result.scalar_one_or_none()
                
                if user_skill:
                    user_skill.mastery_level = mastery
                    user_skill.source = "manual"
                else:
                    user_skill = UserSkill(
                        user_id=current_user.id,
                        skill_id=skill_id,
                        mastery_level=mastery,
                        source="manual"
                    )
                    db.add(user_skill)
                
                updates_made.append(f"Updated skill ID {skill_id}")
    
    await db.commit()
    
    return {
        "message": "Profile updated successfully",
        "updates": updates_made
    }


@router.post("/interaction")
async def record_interaction(
    event: InteractionEvent,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a user interaction that updates the digital twin."""
    result = await digital_twin_service.update_from_interaction(
        db=db,
        user_id=current_user.id,
        event_type=event.event_type,
        skill_ids=event.skill_ids,
        score=event.score,
        duration_seconds=event.duration_seconds
    )
    
    return result


@router.get("/summary")
async def get_profile_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a summary of the digital twin profile."""
    twin = await digital_twin_service.generate_digital_twin(
        db=db,
        user_id=current_user.id
    )
    
    if not twin:
        return {
            "profile_status": "incomplete",
            "message": "No skills recorded yet"
        }
    
    return {
        "profile_status": twin["data_freshness"],
        "total_skills": twin["total_skills"],
        "average_mastery": round(twin["average_mastery"] * 100, 1),
        "profile_completeness": twin["profile_completeness"],
        "top_skill": twin["top_skills"][0]["name"] if twin["top_skills"] else None,
        "main_gap": twin["weakest_skills"][-1]["name"] if twin["weakest_skills"] else None,
        "total_learning_hours": twin["total_learning_hours"],
        "categories_covered": len(twin["category_summaries"])
    }


@router.get("/visualization-data")
async def get_visualization_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get data optimized for visualization."""
    twin = await digital_twin_service.generate_digital_twin(
        db=db,
        user_id=current_user.id
    )
    
    if not twin:
        return {
            "nodes": [],
            "links": [],
            "categories": []
        }
    
    # Format for D3.js or similar visualization library
    nodes = [
        {
            "id": str(node["id"]),
            "name": node["name"],
            "category": node["category"],
            "value": node["mastery_level"],
            "isGap": node["is_gap"],
            "symbolSize": 20 + node["mastery_level"] * 30
        }
        for node in twin["skill_nodes"]
    ]
    
    links = [
        {
            "source": str(conn["source_skill_id"]),
            "target": str(conn["target_skill_id"]),
            "type": conn["relationship_type"],
            "value": conn["strength"]
        }
        for conn in twin["skill_connections"]
    ]
    
    categories = [
        {
            "name": cat["category_name"],
            "itemStyle": {
                "color": _get_category_color(cat["category_name"])
            }
        }
        for cat in twin["category_summaries"]
    ]
    
    return {
        "nodes": nodes,
        "links": links,
        "categories": categories,
        "summary": {
            "totalSkills": twin["total_skills"],
            "averageMastery": twin["average_mastery"],
            "completeness": twin["profile_completeness"]
        }
    }


def _get_category_color(category: str) -> str:
    """Get color for a category."""
    colors = {
        "programming": "#4CAF50",
        "web_development": "#2196F3",
        "data_science": "#9C27B0",
        "database": "#FF9800",
        "cloud": "#00BCD4",
        "devops": "#795548",
        "soft_skills": "#E91E63",
        "Uncategorized": "#9E9E9E"
    }
    return colors.get(category, "#607D8B")
