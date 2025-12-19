"""
Digital Twin Service for managing the skill profile and visualization.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.skill import Skill, SkillCategory, UserSkill, SkillLevel
from app.models.assessment import Assessment
from app.models.learning import LearningRoadmap
from app.services.skill_extraction import skill_extraction_service
from app.services.ai_service import ai_service


class DigitalTwinService:
    """Service for managing the Skill Digital Twin."""
    
    async def generate_digital_twin(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Generate the complete Skill Digital Twin for a user.
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Complete digital twin data for visualization
        """
        # Get user
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Get user skills with skill details
        skills_result = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill).selectinload(Skill.category))
            .where(UserSkill.user_id == user_id)
        )
        user_skills = skills_result.scalars().all()
        
        # Build skill nodes
        skill_nodes = []
        category_stats = {}
        total_mastery = 0
        
        for us in user_skills:
            skill = us.skill
            if not skill:
                continue
            
            category_name = skill.category.name if skill.category else "Uncategorized"
            
            node = {
                "id": skill.id,
                "name": skill.name,
                "category": category_name,
                "mastery_level": us.mastery_level,
                "confidence_score": us.confidence_score,
                "is_gap": us.mastery_level < 0.4,  # Consider < 40% as a gap
                "gap_severity": max(0, 0.5 - us.mastery_level) if us.mastery_level < 0.5 else None,
                "related_skills": skill.related_skills or [],
                "source": us.source,
                "last_updated": us.updated_at
            }
            skill_nodes.append(node)
            total_mastery += us.mastery_level
            
            # Category stats
            if category_name not in category_stats:
                category_stats[category_name] = {
                    "total": 0,
                    "mastered": 0,
                    "total_mastery": 0,
                    "skill_ids": []
                }
            
            category_stats[category_name]["total"] += 1
            category_stats[category_name]["total_mastery"] += us.mastery_level
            category_stats[category_name]["skill_ids"].append(skill.id)
            
            if us.mastery_level >= 0.7:
                category_stats[category_name]["mastered"] += 1
        
        # Build connections between skills
        skill_connections = []
        for us in user_skills:
            skill = us.skill
            if not skill:
                continue
            
            # Prerequisites
            for prereq_id in (skill.prerequisites or []):
                skill_connections.append({
                    "source_skill_id": prereq_id,
                    "target_skill_id": skill.id,
                    "relationship_type": "prerequisite",
                    "strength": 0.8
                })
            
            # Related skills
            for related_id in (skill.related_skills or []):
                # Avoid duplicate connections
                if skill.id < related_id:
                    skill_connections.append({
                        "source_skill_id": skill.id,
                        "target_skill_id": related_id,
                        "relationship_type": "related",
                        "strength": 0.5
                    })
        
        # Calculate summary statistics
        total_skills = len(skill_nodes)
        average_mastery = total_mastery / total_skills if total_skills > 0 else 0
        
        # Sort for top and weakest skills
        sorted_by_mastery = sorted(skill_nodes, key=lambda x: x["mastery_level"], reverse=True)
        top_skills = sorted_by_mastery[:5]
        weakest_skills = sorted_by_mastery[-5:] if len(sorted_by_mastery) > 5 else sorted_by_mastery
        
        # Category summaries
        category_summaries = []
        for cat_name, stats in category_stats.items():
            category_summaries.append({
                "category_id": hash(cat_name) % 10000,  # Generate pseudo-ID
                "category_name": cat_name,
                "total_skills": stats["total"],
                "mastered_skills": stats["mastered"],
                "average_mastery": stats["total_mastery"] / stats["total"] if stats["total"] > 0 else 0,
                "skill_ids": stats["skill_ids"]
            })
        
        # Calculate profile completeness
        profile_completeness = self._calculate_profile_completeness(user, user_skills)
        
        # Get last assessment date
        last_assessment_result = await db.execute(
            select(Assessment.completed_at)
            .where(Assessment.user_id == user_id, Assessment.completed == True)
            .order_by(Assessment.completed_at.desc())
            .limit(1)
        )
        last_assessment = last_assessment_result.scalar_one_or_none()
        
        # Get total learning hours
        learning_result = await db.execute(
            select(func.sum(LearningRoadmap.hours_completed))
            .where(LearningRoadmap.user_id == user_id)
        )
        total_learning_hours = learning_result.scalar_one() or 0
        
        # Determine data freshness
        data_freshness = self._determine_freshness(user_skills, last_assessment)
        
        return {
            "user_id": user_id,
            "user_name": user.full_name,
            "skill_nodes": skill_nodes,
            "skill_connections": skill_connections,
            "total_skills": total_skills,
            "average_mastery": average_mastery,
            "top_skills": top_skills,
            "weakest_skills": weakest_skills,
            "category_summaries": category_summaries,
            "profile_completeness": profile_completeness,
            "last_assessment_date": last_assessment,
            "total_learning_hours": float(total_learning_hours),
            "generated_at": datetime.utcnow(),
            "data_freshness": data_freshness
        }
    
    def _calculate_profile_completeness(
        self,
        user: User,
        user_skills: List[UserSkill]
    ) -> float:
        """Calculate how complete the user's profile is."""
        completeness = 0
        
        # Basic info (30%)
        if user.full_name:
            completeness += 10
        if user.bio:
            completeness += 5
        if user.education_level:
            completeness += 5
        if user.field_of_study:
            completeness += 5
        if user.interests:
            completeness += 5
        
        # Resume/background (30%)
        if user.resume_text:
            completeness += 20
        if user.academic_background:
            completeness += 10
        
        # Skills (40%)
        num_skills = len(user_skills)
        if num_skills >= 20:
            completeness += 40
        elif num_skills >= 10:
            completeness += 30
        elif num_skills >= 5:
            completeness += 20
        elif num_skills >= 1:
            completeness += 10
        
        return min(completeness, 100)
    
    def _determine_freshness(
        self,
        user_skills: List[UserSkill],
        last_assessment: Optional[datetime]
    ) -> str:
        """Determine how fresh the digital twin data is."""
        now = datetime.utcnow()
        
        # Check most recent skill update
        most_recent_skill = max(
            (us.updated_at for us in user_skills if us.updated_at),
            default=None
        )
        
        if not most_recent_skill and not last_assessment:
            return "outdated"
        
        most_recent = max(filter(None, [most_recent_skill, last_assessment]))
        
        days_old = (now - most_recent).days if most_recent else 999
        
        if days_old <= 7:
            return "fresh"
        elif days_old <= 30:
            return "stale"
        else:
            return "outdated"
    
    async def perform_gap_analysis(
        self,
        db: AsyncSession,
        user_id: int,
        target_role_id: Optional[int] = None,
        target_skills: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive gap analysis for a user.
        
        Args:
            db: Database session
            user_id: User ID
            target_role_id: Optional target career role
            target_skills: Optional list of target skill IDs
        
        Returns:
            Detailed gap analysis
        """
        # Get user skills
        skills_result = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill).selectinload(Skill.category))
            .where(UserSkill.user_id == user_id)
        )
        user_skills = skills_result.scalars().all()
        
        user_skill_map = {us.skill_id: us for us in user_skills}
        
        # Determine target skills/levels
        target_requirements = []
        
        if target_role_id:
            from app.models.career import CareerRole, CareerSkillRequirement
            role_result = await db.execute(
                select(CareerSkillRequirement)
                .options(selectinload(CareerSkillRequirement.skill))
                .where(CareerSkillRequirement.career_role_id == target_role_id)
            )
            requirements = role_result.scalars().all()
            
            for req in requirements:
                target_requirements.append({
                    "skill_id": req.skill_id,
                    "skill_name": req.skill.name if req.skill else "Unknown",
                    "required_level": req.required_level,
                    "importance": req.importance,
                    "is_mandatory": req.is_mandatory,
                    "category": req.skill.category.name if req.skill and req.skill.category else "Unknown"
                })
        
        elif target_skills:
            skills_result = await db.execute(
                select(Skill)
                .options(selectinload(Skill.category))
                .where(Skill.id.in_(target_skills))
            )
            skills = skills_result.scalars().all()
            
            for skill in skills:
                target_requirements.append({
                    "skill_id": skill.id,
                    "skill_name": skill.name,
                    "required_level": 0.7,  # Default target
                    "importance": 0.5,
                    "is_mandatory": False,
                    "category": skill.category.name if skill.category else "Unknown"
                })
        
        # Analyze gaps
        critical_gaps = []
        moderate_gaps = []
        minor_gaps = []
        gaps_by_category = {}
        
        for req in target_requirements:
            skill_id = req["skill_id"]
            user_skill = user_skill_map.get(skill_id)
            current_level = user_skill.mastery_level if user_skill else 0
            
            gap = req["required_level"] - current_level
            
            if gap <= 0:
                continue  # No gap
            
            gap_info = {
                "skill_id": skill_id,
                "skill_name": req["skill_name"],
                "current_level": current_level,
                "required_level": req["required_level"],
                "gap": gap,
                "importance": req["importance"],
                "is_mandatory": req["is_mandatory"],
                "category": req["category"]
            }
            
            # Categorize by severity
            if req["is_mandatory"] and gap > 0.3:
                critical_gaps.append(gap_info)
            elif gap > 0.4 or (req["importance"] > 0.7 and gap > 0.2):
                moderate_gaps.append(gap_info)
            else:
                minor_gaps.append(gap_info)
            
            # Group by category
            category = req["category"]
            if category not in gaps_by_category:
                gaps_by_category[category] = []
            gaps_by_category[category].append(gap_info)
        
        # Sort gaps
        critical_gaps.sort(key=lambda x: (x["importance"], x["gap"]), reverse=True)
        moderate_gaps.sort(key=lambda x: (x["importance"], x["gap"]), reverse=True)
        minor_gaps.sort(key=lambda x: (x["importance"], x["gap"]), reverse=True)
        
        # Generate learning priority order
        all_gaps = critical_gaps + moderate_gaps + minor_gaps
        learning_priority = self._calculate_learning_priority(all_gaps)
        
        # Calculate estimated time
        estimated_time = sum(gap["gap"] * 20 * 10 for gap in all_gaps)  # Hours
        
        return {
            "user_id": user_id,
            "total_gaps_identified": len(all_gaps),
            "critical_gaps": critical_gaps,
            "moderate_gaps": moderate_gaps,
            "minor_gaps": minor_gaps,
            "gaps_by_category": gaps_by_category,
            "career_impact": {
                "blocked_by_gaps": len(critical_gaps) > 0,
                "readiness_impact": -sum(g["gap"] * g["importance"] for g in all_gaps) / len(all_gaps) if all_gaps else 0
            },
            "learning_priority_order": learning_priority,
            "immediate_actions": [
                f"Focus on {gap['skill_name']}" for gap in critical_gaps[:3]
            ],
            "short_term_goals": [
                {"skill": gap["skill_name"], "target_level": gap["required_level"], "timeline": "1-3 months"}
                for gap in critical_gaps[:2] + moderate_gaps[:2]
            ],
            "long_term_goals": [
                {"skill": gap["skill_name"], "target_level": gap["required_level"], "timeline": "3-12 months"}
                for gap in moderate_gaps[2:] + minor_gaps
            ],
            "recommended_resources": [],  # Will be populated by learning service
            "estimated_time_to_close_gaps": estimated_time,
            "analysis_date": datetime.utcnow(),
            "confidence_level": 0.8
        }
    
    def _calculate_learning_priority(
        self,
        gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate optimal learning order based on prerequisites and importance."""
        # Score each gap
        priority_list = []
        
        for i, gap in enumerate(gaps):
            score = (
                gap["importance"] * 0.4 +
                (1 if gap["is_mandatory"] else 0) * 0.3 +
                gap["gap"] * 0.2 +
                (len(gaps) - i) / len(gaps) * 0.1  # Original order bonus
            )
            
            priority_list.append({
                "skill_id": gap["skill_id"],
                "skill_name": gap["skill_name"],
                "priority_score": score,
                "reason": "Mandatory skill" if gap["is_mandatory"] else "High importance" if gap["importance"] > 0.7 else "Significant gap"
            })
        
        priority_list.sort(key=lambda x: x["priority_score"], reverse=True)
        return priority_list
    
    async def update_from_interaction(
        self,
        db: AsyncSession,
        user_id: int,
        event_type: str,
        skill_ids: List[int],
        score: Optional[float] = None,
        duration_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update the digital twin based on user interaction.
        
        Args:
            db: Database session
            user_id: User ID
            event_type: Type of interaction
            skill_ids: Skills involved
            score: Optional score achieved
            duration_seconds: Optional duration of activity
        
        Returns:
            Summary of updates made
        """
        updates = []
        
        for skill_id in skill_ids:
            # Get or create user skill
            result = await db.execute(
                select(UserSkill)
                .where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
            )
            user_skill = result.scalar_one_or_none()
            
            if not user_skill:
                user_skill = UserSkill(
                    user_id=user_id,
                    skill_id=skill_id,
                    mastery_level=0.1,
                    confidence_score=0.3
                )
                db.add(user_skill)
            
            # Calculate update based on event type
            mastery_delta = 0
            confidence_delta = 0
            
            if event_type == "course_completion":
                mastery_delta = 0.15
                confidence_delta = 0.1
            elif event_type == "assessment":
                if score is not None:
                    # Assessment directly informs mastery
                    user_skill.mastery_level = (user_skill.mastery_level + score) / 2
                    confidence_delta = 0.2  # High confidence from assessment
            elif event_type == "resource_viewed":
                mastery_delta = 0.02
                confidence_delta = 0.01
            elif event_type == "practice":
                mastery_delta = 0.05 * (score or 0.5)
                confidence_delta = 0.05
            
            # Apply updates
            user_skill.mastery_level = min(1.0, user_skill.mastery_level + mastery_delta)
            user_skill.confidence_score = min(1.0, user_skill.confidence_score + confidence_delta)
            user_skill.last_assessed = datetime.utcnow()
            user_skill.source = event_type
            
            # Update skill level enum
            if user_skill.mastery_level >= 0.9:
                user_skill.skill_level = SkillLevel.EXPERT
            elif user_skill.mastery_level >= 0.7:
                user_skill.skill_level = SkillLevel.ADVANCED
            elif user_skill.mastery_level >= 0.5:
                user_skill.skill_level = SkillLevel.INTERMEDIATE
            elif user_skill.mastery_level >= 0.3:
                user_skill.skill_level = SkillLevel.BEGINNER
            else:
                user_skill.skill_level = SkillLevel.NOVICE
            
            updates.append({
                "skill_id": skill_id,
                "new_mastery": user_skill.mastery_level,
                "new_confidence": user_skill.confidence_score
            })
        
        await db.commit()
        
        return {
            "user_id": user_id,
            "event_type": event_type,
            "updates_applied": updates,
            "timestamp": datetime.utcnow()
        }


# Singleton instance
digital_twin_service = DigitalTwinService()
