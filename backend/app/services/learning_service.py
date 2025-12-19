"""
Learning Service for roadmap generation and resource management.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.learning import LearningRoadmap, LearningModule, LearningResource, ModuleStatus, ResourceType
from app.models.skill import Skill, UserSkill
from app.services.ai_service import ai_service
from app.services.youtube_service import youtube_service


class LearningService:
    """Service for learning roadmap and resource management."""
    
    async def generate_learning_roadmap(
        self,
        db: AsyncSession,
        user_id: int,
        target_skills: Optional[List[int]] = None,
        target_career_role: Optional[str] = None,
        skill_gaps: Optional[List[Dict[str, Any]]] = None,
        available_hours_per_week: int = 10,
        preferred_learning_style: str = "video"
    ) -> LearningRoadmap:
        """
        Generate a personalized learning roadmap.
        
        Args:
            db: Database session
            user_id: User ID
            target_skills: Target skill IDs
            target_career_role: Target career role
            skill_gaps: Pre-identified skill gaps
            available_hours_per_week: Hours available per week
            preferred_learning_style: Preferred learning style
        
        Returns:
            Generated learning roadmap
        """
        # Get user's current skills
        current_skills_result = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill))
            .where(UserSkill.user_id == user_id)
        )
        current_skills = current_skills_result.scalars().all()
        
        current_skills_data = [
            {
                "skill_id": us.skill_id,
                "skill_name": us.skill.name if us.skill else "Unknown",
                "mastery_level": us.mastery_level
            }
            for us in current_skills
        ]
        
        # Prepare skill gaps data
        if not skill_gaps and target_skills:
            skill_gaps = []
            for skill_id in target_skills:
                skill_result = await db.execute(
                    select(Skill).where(Skill.id == skill_id)
                )
                skill = skill_result.scalar_one_or_none()
                
                current = next(
                    (cs for cs in current_skills if cs.skill_id == skill_id),
                    None
                )
                current_level = current.mastery_level if current else 0
                
                skill_gaps.append({
                    "skill_id": skill_id,
                    "skill_name": skill.name if skill else "Unknown",
                    "current_level": current_level,
                    "required_level": 0.8
                })
        
        # Generate roadmap using AI
        ai_roadmap = await ai_service.generate_learning_roadmap(
            skill_gaps=skill_gaps or [],
            current_skills=current_skills_data,
            target_role=target_career_role,
            learning_style=preferred_learning_style
        )
        
        # Create roadmap
        roadmap = LearningRoadmap(
            user_id=user_id,
            title=ai_roadmap.get("title", f"Learning Roadmap for {target_career_role or 'Skill Development'}"),
            description=ai_roadmap.get("description", ""),
            target_skills=target_skills or [],
            target_career_role=target_career_role,
            estimated_hours=ai_roadmap.get("total_estimated_hours", 0),
            is_active=True,
            generated_by_ai=True,
            generation_context={
                "skill_gaps": skill_gaps,
                "learning_style": preferred_learning_style,
                "hours_per_week": available_hours_per_week
            }
        )
        
        db.add(roadmap)
        await db.flush()
        
        # Create modules
        for i, module_data in enumerate(ai_roadmap.get("modules", [])):
            module = await self._create_module(
                db,
                roadmap.id,
                module_data,
                i,
                preferred_learning_style
            )
            db.add(module)
        
        await db.commit()
        await db.refresh(roadmap)
        
        return roadmap
    
    async def _create_module(
        self,
        db: AsyncSession,
        roadmap_id: int,
        module_data: Dict[str, Any],
        order_index: int,
        learning_style: str
    ) -> LearningModule:
        """Create a learning module with resources."""
        # Generate topic overview
        topic = module_data.get("title", "Learning Module")
        overview = await ai_service.generate_topic_overview(topic)
        
        module = LearningModule(
            roadmap_id=roadmap_id,
            title=module_data.get("title", f"Module {order_index + 1}"),
            description=module_data.get("description", ""),
            topic_overview=overview.get("overview", ""),
            key_concepts=overview.get("key_concepts", []),
            learning_objectives=overview.get("learning_objectives", []),
            estimated_hours=module_data.get("estimated_hours", 5),
            order_index=order_index,
            status=ModuleStatus.NOT_STARTED
        )
        
        db.add(module)
        await db.flush()
        
        # Get YouTube resources
        search_keywords = module_data.get("search_keywords", [topic])
        resources = await self._get_module_resources(
            db,
            module.id,
            search_keywords,
            learning_style
        )
        
        for resource in resources:
            db.add(resource)
        
        return module
    
    async def _get_module_resources(
        self,
        db: AsyncSession,
        module_id: int,
        search_keywords: List[str],
        learning_style: str
    ) -> List[LearningResource]:
        """Get learning resources for a module."""
        resources = []
        
        for i, keyword in enumerate(search_keywords[:3]):  # Limit to 3 search terms
            videos = await youtube_service.get_learning_videos(
                topic=keyword,
                skill_level="beginner" if i == 0 else "intermediate",
                max_results=2,
                duration_preference="medium"
            )
            
            for j, video in enumerate(videos):
                resource = LearningResource(
                    module_id=module_id,
                    title=video["title"],
                    description=video["description"][:500] if video.get("description") else "",
                    resource_type=ResourceType.VIDEO,
                    url=video["url"],
                    platform="youtube",
                    youtube_video_id=video["video_id"],
                    youtube_channel=video["channel_title"],
                    duration_seconds=video["duration_seconds"],
                    thumbnail_url=video["thumbnail_url"],
                    relevance_score=video.get("relevance_score", 0.5),
                    quality_score=video.get("quality_score", 0.5),
                    view_count=video["view_count"],
                    like_count=video.get("like_count"),
                    order_index=i * 2 + j,
                    ai_recommended=True,
                    recommendation_reason=f"Relevant to {keyword}"
                )
                resources.append(resource)
        
        return resources
    
    async def get_roadmap_with_details(
        self,
        db: AsyncSession,
        roadmap_id: int,
        user_id: int
    ) -> Optional[LearningRoadmap]:
        """Get a roadmap with all modules and resources."""
        result = await db.execute(
            select(LearningRoadmap)
            .options(
                selectinload(LearningRoadmap.modules)
                .selectinload(LearningModule.resources)
            )
            .where(
                LearningRoadmap.id == roadmap_id,
                LearningRoadmap.user_id == user_id
            )
        )
        
        return result.scalar_one_or_none()
    
    async def update_progress(
        self,
        db: AsyncSession,
        user_id: int,
        roadmap_id: Optional[int] = None,
        module_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        progress: Optional[float] = None,
        completed: bool = False
    ) -> Dict[str, Any]:
        """
        Update learning progress.
        
        Args:
            db: Database session
            user_id: User ID
            roadmap_id: Roadmap ID
            module_id: Module ID
            resource_id: Resource ID
            progress: Progress value (0-1)
            completed: Whether item is completed
        
        Returns:
            Updated progress summary
        """
        if resource_id:
            # Update resource progress
            result = await db.execute(
                select(LearningResource)
                .options(selectinload(LearningResource.module))
                .where(LearningResource.id == resource_id)
            )
            resource = result.scalar_one_or_none()
            
            if resource:
                if progress is not None:
                    resource.watch_progress = progress
                if completed:
                    resource.completed = True
                
                # Update parent module progress
                module = resource.module
                if module:
                    await self._update_module_progress(db, module)
        
        elif module_id:
            # Update module status
            result = await db.execute(
                select(LearningModule)
                .options(selectinload(LearningModule.roadmap))
                .where(LearningModule.id == module_id)
            )
            module = result.scalar_one_or_none()
            
            if module:
                if completed:
                    module.status = ModuleStatus.COMPLETED
                    module.completed_at = datetime.utcnow()
                    module.progress = 1.0
                elif progress is not None:
                    module.progress = progress
                    if progress > 0 and module.status == ModuleStatus.NOT_STARTED:
                        module.status = ModuleStatus.IN_PROGRESS
                        module.started_at = datetime.utcnow()
                
                # Update parent roadmap progress
                await self._update_roadmap_progress(db, module.roadmap)
        
        await db.commit()
        
        return {
            "updated": True,
            "resource_id": resource_id,
            "module_id": module_id,
            "roadmap_id": roadmap_id,
            "timestamp": datetime.utcnow()
        }
    
    async def _update_module_progress(self, db: AsyncSession, module: LearningModule):
        """Update module progress based on resources."""
        result = await db.execute(
            select(LearningResource)
            .where(LearningResource.module_id == module.id)
        )
        resources = result.scalars().all()
        
        if resources:
            completed_count = sum(1 for r in resources if r.completed)
            progress_sum = sum(r.watch_progress for r in resources)
            
            module.progress = progress_sum / len(resources)
            
            if completed_count == len(resources):
                module.status = ModuleStatus.COMPLETED
                module.completed_at = datetime.utcnow()
            elif completed_count > 0 or module.progress > 0:
                module.status = ModuleStatus.IN_PROGRESS
                if not module.started_at:
                    module.started_at = datetime.utcnow()
    
    async def _update_roadmap_progress(self, db: AsyncSession, roadmap: LearningRoadmap):
        """Update roadmap progress based on modules."""
        result = await db.execute(
            select(LearningModule)
            .where(LearningModule.roadmap_id == roadmap.id)
        )
        modules = result.scalars().all()
        
        if modules:
            progress_sum = sum(m.progress for m in modules)
            roadmap.overall_progress = progress_sum / len(modules)
            
            # Calculate hours completed
            completed_hours = sum(
                m.estimated_hours or 0
                for m in modules
                if m.status == ModuleStatus.COMPLETED
            )
            in_progress_hours = sum(
                (m.estimated_hours or 0) * m.progress
                for m in modules
                if m.status == ModuleStatus.IN_PROGRESS
            )
            
            roadmap.hours_completed = completed_hours + in_progress_hours
            
            # Check if roadmap is complete
            if all(m.status == ModuleStatus.COMPLETED for m in modules):
                roadmap.completed = True
                roadmap.completed_at = datetime.utcnow()
    
    async def get_recommended_next_resource(
        self,
        db: AsyncSession,
        user_id: int,
        roadmap_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get the next recommended resource for a user."""
        roadmap = await self.get_roadmap_with_details(db, roadmap_id, user_id)
        
        if not roadmap:
            return None
        
        # Find first incomplete module
        for module in sorted(roadmap.modules, key=lambda m: m.order_index):
            if module.status != ModuleStatus.COMPLETED:
                # Find first incomplete resource
                for resource in sorted(module.resources, key=lambda r: r.order_index):
                    if not resource.completed:
                        return {
                            "module": {
                                "id": module.id,
                                "title": module.title,
                                "progress": module.progress
                            },
                            "resource": {
                                "id": resource.id,
                                "title": resource.title,
                                "url": resource.url,
                                "type": resource.resource_type.value,
                                "duration_seconds": resource.duration_seconds
                            }
                        }
        
        return None


# Singleton instance
learning_service = LearningService()
