"""
Career Service for job role matching and alignment analysis.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.career import CareerRole, CareerSkillRequirement, CareerAlignment
from app.models.skill import UserSkill, Skill
from app.models.user import User
from app.services.ai_service import ai_service


class CareerService:
    """Service for career analysis and alignment calculations."""
    
    async def calculate_career_alignment(
        self,
        db: AsyncSession,
        user_id: int,
        career_role_id: int
    ) -> Dict[str, Any]:
        """
        Calculate how well a user aligns with a career role.
        
        Args:
            db: Database session
            user_id: User ID
            career_role_id: Career role ID
        
        Returns:
            Career alignment details
        """
        # Get user skills
        user_skills_result = await db.execute(
            select(UserSkill)
            .options(selectinload(UserSkill.skill))
            .where(UserSkill.user_id == user_id)
        )
        user_skills = user_skills_result.scalars().all()
        
        # Get career role with requirements
        career_result = await db.execute(
            select(CareerRole)
            .options(selectinload(CareerRole.skill_requirements).selectinload(CareerSkillRequirement.skill))
            .where(CareerRole.id == career_role_id)
        )
        career_role = career_result.scalar_one_or_none()
        
        if not career_role:
            return None
        
        # Build user skill map
        user_skill_map = {
            us.skill_id: {
                "mastery_level": us.mastery_level,
                "skill_name": us.skill.name if us.skill else "Unknown"
            }
            for us in user_skills
        }
        
        # Calculate alignment
        skill_gaps = []
        strengths = []
        total_weighted_score = 0
        total_weight = 0
        mandatory_met = True
        
        for req in career_role.skill_requirements:
            skill_id = req.skill_id
            required_level = req.required_level
            importance = req.importance
            is_mandatory = req.is_mandatory
            skill_name = req.skill.name if req.skill else "Unknown"
            
            user_skill = user_skill_map.get(skill_id, {"mastery_level": 0, "skill_name": skill_name})
            current_level = user_skill["mastery_level"]
            
            gap = max(0, required_level - current_level)
            excess = max(0, current_level - required_level)
            
            # Calculate weighted contribution
            if gap > 0:
                skill_gaps.append({
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "current_level": current_level,
                    "required_level": required_level,
                    "gap": gap,
                    "importance": importance,
                    "is_mandatory": is_mandatory
                })
                score = current_level / required_level if required_level > 0 else 0
                if is_mandatory and gap > 0.2:  # Significant gap in mandatory skill
                    mandatory_met = False
            else:
                if excess > 0.1:  # Significantly exceeds requirements
                    strengths.append({
                        "skill_id": skill_id,
                        "skill_name": skill_name,
                        "current_level": current_level,
                        "required_level": required_level,
                        "excess": excess,
                        "importance": importance
                    })
                score = 1.0
            
            total_weighted_score += score * importance
            total_weight += importance
        
        # Calculate overall readiness
        skill_match_score = total_weighted_score / total_weight if total_weight > 0 else 0
        overall_readiness = skill_match_score * (0.9 if mandatory_met else 0.6)
        
        # Get user for experience matching
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        experience_match = self._calculate_experience_match(user, career_role) if user else 0.5
        
        # Adjust overall readiness with experience
        overall_readiness = overall_readiness * 0.8 + experience_match * 0.2
        
        # Sort gaps by priority
        skill_gaps.sort(key=lambda x: (x["is_mandatory"], x["importance"], x["gap"]), reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(skill_gaps, career_role)
        priority_skills = [
            {"skill_id": g["skill_id"], "skill_name": g["skill_name"], "gap": g["gap"]}
            for g in skill_gaps[:5]
        ]
        
        # Estimate time to ready
        estimated_time = self._estimate_time_to_ready(skill_gaps)
        
        return {
            "user_id": user_id,
            "career_role_id": career_role_id,
            "overall_readiness": overall_readiness,
            "skill_match_score": skill_match_score,
            "experience_match_score": experience_match,
            "skill_gaps": skill_gaps,
            "strengths": strengths,
            "upskilling_recommendations": recommendations,
            "estimated_time_to_ready": estimated_time,
            "priority_skills": priority_skills
        }
    
    def _calculate_experience_match(self, user: User, career_role: CareerRole) -> float:
        """Calculate experience level match."""
        user_years = user.years_of_experience or 0
        
        experience_requirements = {
            "entry": (0, 1),
            "junior": (0, 2),
            "mid": (2, 5),
            "senior": (5, 10),
            "lead": (7, 15),
            "principal": (10, 20)
        }
        
        role_level = career_role.experience_level.value if career_role.experience_level else "mid"
        min_years, max_years = experience_requirements.get(role_level, (2, 5))
        
        if user_years < min_years:
            return max(0, 0.5 - (min_years - user_years) * 0.1)
        elif user_years > max_years:
            return max(0.7, 1.0 - (user_years - max_years) * 0.05)
        else:
            return 1.0
    
    def _generate_recommendations(
        self,
        skill_gaps: List[Dict[str, Any]],
        career_role: CareerRole
    ) -> List[Dict[str, Any]]:
        """Generate upskilling recommendations."""
        recommendations = []
        
        # Mandatory skills first
        mandatory_gaps = [g for g in skill_gaps if g["is_mandatory"]]
        for gap in mandatory_gaps[:3]:
            recommendations.append({
                "type": "mandatory_skill",
                "skill_name": gap["skill_name"],
                "priority": "high",
                "action": f"Focus on {gap['skill_name']} - this is a mandatory requirement",
                "target_level": gap["required_level"],
                "current_gap": gap["gap"]
            })
        
        # High importance skills
        important_gaps = [g for g in skill_gaps if g["importance"] > 0.7 and not g["is_mandatory"]]
        for gap in important_gaps[:2]:
            recommendations.append({
                "type": "important_skill",
                "skill_name": gap["skill_name"],
                "priority": "medium",
                "action": f"Develop {gap['skill_name']} to strengthen your profile",
                "target_level": gap["required_level"],
                "current_gap": gap["gap"]
            })
        
        return recommendations
    
    def _estimate_time_to_ready(self, skill_gaps: List[Dict[str, Any]]) -> float:
        """Estimate hours needed to close skill gaps."""
        total_hours = 0
        
        # Base hours per gap percentage point
        hours_per_gap_point = 20  # 20 hours to improve 0.1 mastery level
        
        for gap in skill_gaps:
            gap_amount = gap["gap"]
            importance = gap["importance"]
            
            # More important skills might need more thorough learning
            hours_for_skill = gap_amount * hours_per_gap_point * 10 * (1 + importance * 0.5)
            total_hours += hours_for_skill
        
        return round(total_hours, 1)
    
    async def analyze_multiple_careers(
        self,
        db: AsyncSession,
        user_id: int,
        career_role_ids: Optional[List[int]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Analyze user fit across multiple career roles.
        
        Args:
            db: Database session
            user_id: User ID
            career_role_ids: Specific roles to analyze (or all if None)
            limit: Maximum number of roles to return
        
        Returns:
            List of career alignments sorted by readiness
        """
        if career_role_ids:
            query = select(CareerRole).where(CareerRole.id.in_(career_role_ids))
        else:
            query = select(CareerRole).limit(50)  # Analyze up to 50 roles
        
        result = await db.execute(query)
        career_roles = result.scalars().all()
        
        alignments = []
        for role in career_roles:
            alignment = await self.calculate_career_alignment(db, user_id, role.id)
            if alignment:
                alignment["career_role_title"] = role.title
                alignment["career_role_description"] = role.description
                alignments.append(alignment)
        
        # Sort by overall readiness
        alignments.sort(key=lambda x: x["overall_readiness"], reverse=True)
        
        return alignments[:limit]
    
    async def get_career_recommendations(
        self,
        db: AsyncSession,
        user_id: int,
        min_readiness: float = 0.3
    ) -> Dict[str, Any]:
        """
        Get personalized career recommendations for a user.
        
        Args:
            db: Database session
            user_id: User ID
            min_readiness: Minimum readiness threshold for recommendations
        
        Returns:
            Career recommendations with analysis
        """
        alignments = await self.analyze_multiple_careers(db, user_id, limit=20)
        
        # Filter by minimum readiness
        viable_careers = [a for a in alignments if a["overall_readiness"] >= min_readiness]
        stretch_careers = [a for a in alignments if 0.2 <= a["overall_readiness"] < min_readiness]
        
        # Identify common skill gaps across top careers
        all_gaps = {}
        for alignment in viable_careers[:5]:
            for gap in alignment["skill_gaps"]:
                skill_name = gap["skill_name"]
                if skill_name not in all_gaps:
                    all_gaps[skill_name] = {"count": 0, "total_gap": 0, "importance_sum": 0}
                all_gaps[skill_name]["count"] += 1
                all_gaps[skill_name]["total_gap"] += gap["gap"]
                all_gaps[skill_name]["importance_sum"] += gap["importance"]
        
        # Prioritize skills that appear in multiple career paths
        priority_skills = sorted(
            all_gaps.items(),
            key=lambda x: (x[1]["count"], x[1]["importance_sum"]),
            reverse=True
        )[:5]
        
        return {
            "user_id": user_id,
            "ready_careers": viable_careers[:5],
            "stretch_careers": stretch_careers[:3],
            "priority_skills_to_develop": [
                {"skill_name": skill, "appears_in_careers": data["count"], "average_gap": data["total_gap"] / data["count"]}
                for skill, data in priority_skills
            ],
            "analysis_timestamp": datetime.utcnow()
        }


# Singleton instance
career_service = CareerService()
