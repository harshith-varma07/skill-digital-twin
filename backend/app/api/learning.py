"""
Learning API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.learning import LearningRoadmap, LearningModule, LearningResource
from app.schemas.learning import (
    LearningRoadmapCreate, LearningRoadmapResponse, RoadmapGenerationRequest,
    RoadmapProgressUpdate, YouTubeRecommendationRequest, YouTubeVideoResponse
)
from app.services.learning_service import learning_service
from app.services.youtube_service import youtube_service

router = APIRouter()


@router.get("/roadmaps", response_model=List[LearningRoadmapResponse])
async def list_roadmaps(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's learning roadmaps."""
    query = select(LearningRoadmap).options(
        selectinload(LearningRoadmap.modules).selectinload(LearningModule.resources)
    ).where(LearningRoadmap.user_id == current_user.id)
    
    if active_only:
        query = query.where(LearningRoadmap.is_active == True)
    
    query = query.order_by(LearningRoadmap.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/roadmaps/{roadmap_id}", response_model=LearningRoadmapResponse)
async def get_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get roadmap details."""
    roadmap = await learning_service.get_roadmap_with_details(
        db=db,
        roadmap_id=roadmap_id,
        user_id=current_user.id
    )
    
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found"
        )
    
    return roadmap


@router.post("/roadmaps/generate", response_model=LearningRoadmapResponse)
async def generate_roadmap(
    request: RoadmapGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a personalized learning roadmap."""
    roadmap = await learning_service.generate_learning_roadmap(
        db=db,
        user_id=current_user.id,
        target_skills=request.target_skills,
        target_career_role=request.target_career_role,
        skill_gaps=request.skill_gaps,
        available_hours_per_week=request.available_hours_per_week,
        preferred_learning_style=request.preferred_learning_style
    )
    
    # Reload with full details
    return await learning_service.get_roadmap_with_details(
        db=db,
        roadmap_id=roadmap.id,
        user_id=current_user.id
    )


@router.post("/roadmaps/{roadmap_id}/progress")
async def update_roadmap_progress(
    roadmap_id: int,
    update: RoadmapProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update learning progress."""
    result = await learning_service.update_progress(
        db=db,
        user_id=current_user.id,
        roadmap_id=roadmap_id,
        module_id=update.module_id,
        resource_id=update.resource_id,
        progress=update.progress,
        completed=update.completed or False
    )
    
    return result


@router.get("/roadmaps/{roadmap_id}/next")
async def get_next_resource(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get next recommended resource."""
    next_resource = await learning_service.get_recommended_next_resource(
        db=db,
        user_id=current_user.id,
        roadmap_id=roadmap_id
    )
    
    if not next_resource:
        return {"message": "No more resources to complete", "completed": True}
    
    return next_resource


@router.delete("/roadmaps/{roadmap_id}")
async def delete_roadmap(
    roadmap_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a learning roadmap."""
    result = await db.execute(
        select(LearningRoadmap)
        .where(LearningRoadmap.id == roadmap_id, LearningRoadmap.user_id == current_user.id)
    )
    roadmap = result.scalar_one_or_none()
    
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found"
        )
    
    await db.delete(roadmap)
    await db.commit()
    
    return {"message": "Roadmap deleted"}


@router.post("/youtube/search", response_model=List[YouTubeVideoResponse])
async def search_youtube_videos(
    request: YouTubeRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """Search for YouTube learning videos."""
    videos = await youtube_service.get_learning_videos(
        topic=request.topic,
        skill_level=request.skill_level,
        max_results=request.max_results,
        duration_preference=request.duration_preference
    )
    
    return [
        YouTubeVideoResponse(
            video_id=v["video_id"],
            title=v["title"],
            description=v["description"],
            channel_title=v["channel_title"],
            thumbnail_url=v["thumbnail_url"],
            duration_seconds=v["duration_seconds"],
            view_count=v["view_count"],
            like_count=v.get("like_count"),
            relevance_score=v.get("relevance_score", 0.5),
            url=v["url"]
        )
        for v in videos
    ]


@router.post("/modules/{module_id}/complete")
async def mark_module_complete(
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a module as complete."""
    result = await learning_service.update_progress(
        db=db,
        user_id=current_user.id,
        module_id=module_id,
        completed=True
    )
    
    return result


@router.post("/resources/{resource_id}/progress")
async def update_resource_progress(
    resource_id: int,
    progress: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update resource progress (e.g., video watch progress)."""
    result = await learning_service.update_progress(
        db=db,
        user_id=current_user.id,
        resource_id=resource_id,
        progress=progress,
        completed=progress >= 0.9  # Auto-complete at 90%
    )
    
    return result
