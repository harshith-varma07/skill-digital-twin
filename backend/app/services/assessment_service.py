"""
Assessment Service for managing diagnostic tests and skill validation.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.assessment import Assessment, AssessmentQuestion, AssessmentResponse, AssessmentType, QuestionType
from app.models.skill import Skill, UserSkill
from app.services.ai_service import ai_service


class AssessmentService:
    """Service for assessment management and evaluation."""
    
    async def create_diagnostic_assessment(
        self,
        db: AsyncSession,
        user_id: int,
        skill_areas: Optional[List[str]] = None,
        num_questions: int = 10,
        difficulty: str = "adaptive"
    ) -> Assessment:
        """
        Create a diagnostic assessment for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skill_areas: Areas to focus on
            num_questions: Number of questions
            difficulty: Difficulty level
        
        Returns:
            Created assessment
        """
        # Get target skills
        if skill_areas:
            skills_result = await db.execute(
                select(Skill).where(Skill.name.in_(skill_areas))
            )
            skills = skills_result.scalars().all()
            target_skill_ids = [s.id for s in skills]
        else:
            # Get user's existing skills for adaptive assessment
            user_skills_result = await db.execute(
                select(UserSkill).where(UserSkill.user_id == user_id)
            )
            user_skills = user_skills_result.scalars().all()
            target_skill_ids = [us.skill_id for us in user_skills]
        
        # Create assessment
        assessment = Assessment(
            user_id=user_id,
            title="Diagnostic Assessment",
            description="Comprehensive skill evaluation",
            assessment_type=AssessmentType.DIAGNOSTIC,
            target_skills=target_skill_ids,
            passing_score=0.7,
            max_attempts=3
        )
        
        db.add(assessment)
        await db.flush()  # Get the ID
        
        # Generate questions using AI
        questions = await self._generate_assessment_questions(
            db,
            assessment.id,
            target_skill_ids,
            num_questions,
            difficulty
        )
        
        for q in questions:
            db.add(q)
        
        await db.commit()
        await db.refresh(assessment)
        
        return assessment
    
    async def _generate_assessment_questions(
        self,
        db: AsyncSession,
        assessment_id: int,
        skill_ids: List[int],
        num_questions: int,
        difficulty: str
    ) -> List[AssessmentQuestion]:
        """Generate questions for an assessment."""
        questions = []
        
        # Get skills
        skills_result = await db.execute(
            select(Skill).where(Skill.id.in_(skill_ids))
        )
        skills = skills_result.scalars().all()
        
        if not skills:
            return questions
        
        # Distribute questions across skills
        questions_per_skill = max(1, num_questions // len(skills))
        
        difficulty_map = {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.7,
            "adaptive": 0.5
        }
        base_difficulty = difficulty_map.get(difficulty, 0.5)
        
        order_index = 0
        for skill in skills:
            # Generate questions for this skill
            ai_questions = await ai_service.generate_questions(
                skill_name=skill.name,
                skill_description=skill.description or "",
                difficulty=base_difficulty,
                question_type="multiple_choice",
                num_questions=questions_per_skill
            )
            
            for q_data in ai_questions:
                question = AssessmentQuestion(
                    assessment_id=assessment_id,
                    question_text=q_data.get("question_text", ""),
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    options=q_data.get("options", []),
                    correct_answer=q_data.get("correct_answer", ""),
                    explanation=q_data.get("explanation", ""),
                    skill_id=skill.id,
                    difficulty_level=q_data.get("difficulty", base_difficulty),
                    points=1.0,
                    order_index=order_index,
                    generated_by_ai=True
                )
                questions.append(question)
                order_index += 1
        
        return questions
    
    async def submit_response(
        self,
        db: AsyncSession,
        assessment_id: int,
        question_id: int,
        user_id: int,
        response_text: Optional[str] = None,
        selected_option: Optional[int] = None,
        time_spent_seconds: Optional[int] = None
    ) -> AssessmentResponse:
        """
        Submit a response to an assessment question.
        
        Args:
            db: Database session
            assessment_id: Assessment ID
            question_id: Question ID
            user_id: User ID
            response_text: Text response for open-ended questions
            selected_option: Selected option index for multiple choice
            time_spent_seconds: Time spent on question
        
        Returns:
            Assessment response with evaluation
        """
        # Get the question
        question_result = await db.execute(
            select(AssessmentQuestion).where(AssessmentQuestion.id == question_id)
        )
        question = question_result.scalar_one_or_none()
        
        if not question:
            raise ValueError("Question not found")
        
        # Evaluate response
        is_correct = False
        score = 0.0
        ai_feedback = None
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            # Check selected option
            if selected_option is not None and question.options:
                selected_answer = question.options[selected_option] if selected_option < len(question.options) else ""
                is_correct = selected_answer == question.correct_answer
                score = 1.0 if is_correct else 0.0
        
        elif question.question_type == QuestionType.SHORT_ANSWER or question.question_type == QuestionType.ESSAY:
            # Use AI to evaluate
            if response_text:
                skill_result = await db.execute(
                    select(Skill).where(Skill.id == question.skill_id)
                )
                skill = skill_result.scalar_one_or_none()
                
                evaluation = await ai_service.evaluate_response(
                    question=question.question_text,
                    user_response=response_text,
                    correct_answer=question.correct_answer,
                    skill_context=skill.name if skill else ""
                )
                
                is_correct = evaluation.get("is_correct", False)
                score = evaluation.get("score", 0.0)
                ai_feedback = evaluation.get("feedback", "")
        
        # Create response record
        response = AssessmentResponse(
            assessment_id=assessment_id,
            question_id=question_id,
            user_id=user_id,
            response_text=response_text,
            selected_option=selected_option,
            is_correct=is_correct,
            score=score,
            ai_feedback=ai_feedback,
            time_spent_seconds=time_spent_seconds
        )
        
        db.add(response)
        await db.commit()
        await db.refresh(response)
        
        return response
    
    async def complete_assessment(
        self,
        db: AsyncSession,
        assessment_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Complete an assessment and calculate results.
        
        Args:
            db: Database session
            assessment_id: Assessment ID
            user_id: User ID
        
        Returns:
            Assessment results
        """
        # Get assessment with questions and responses
        assessment_result = await db.execute(
            select(Assessment)
            .options(
                selectinload(Assessment.questions),
                selectinload(Assessment.responses)
            )
            .where(Assessment.id == assessment_id, Assessment.user_id == user_id)
        )
        assessment = assessment_result.scalar_one_or_none()
        
        if not assessment:
            raise ValueError("Assessment not found")
        
        # Calculate score
        total_points = sum(q.points for q in assessment.questions)
        earned_points = sum(r.score for r in assessment.responses)
        
        overall_score = earned_points / total_points if total_points > 0 else 0
        
        # Calculate per-skill breakdown
        skill_scores = {}
        for response in assessment.responses:
            question = next((q for q in assessment.questions if q.id == response.question_id), None)
            if question and question.skill_id:
                if question.skill_id not in skill_scores:
                    skill_scores[question.skill_id] = {"total": 0, "earned": 0}
                skill_scores[question.skill_id]["total"] += question.points
                skill_scores[question.skill_id]["earned"] += response.score
        
        skill_breakdown = {
            skill_id: data["earned"] / data["total"] if data["total"] > 0 else 0
            for skill_id, data in skill_scores.items()
        }
        
        # Identify gaps (skills with score < 60%)
        skill_gaps = []
        strengths = []
        
        for skill_id, score in skill_breakdown.items():
            skill_result = await db.execute(
                select(Skill).where(Skill.id == skill_id)
            )
            skill = skill_result.scalar_one_or_none()
            skill_name = skill.name if skill else f"Skill {skill_id}"
            
            if score < 0.6:
                skill_gaps.append({
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "score": score,
                    "gap": 0.6 - score
                })
            else:
                strengths.append({
                    "skill_id": skill_id,
                    "skill_name": skill_name,
                    "score": score
                })
        
        # Update assessment
        assessment.score = overall_score
        assessment.completed = True
        assessment.completed_at = datetime.utcnow()
        assessment.attempts += 1
        assessment.skill_gaps_identified = skill_gaps
        
        # Update user skills based on assessment
        await self._update_user_skills_from_assessment(db, user_id, skill_breakdown)
        
        await db.commit()
        
        return {
            "assessment_id": assessment_id,
            "overall_score": overall_score,
            "passed": overall_score >= assessment.passing_score,
            "skill_breakdown": skill_breakdown,
            "skill_gaps": skill_gaps,
            "strengths": strengths,
            "recommendations": [
                f"Focus on improving {gap['skill_name']}" for gap in skill_gaps[:3]
            ],
            "completed_at": assessment.completed_at
        }
    
    async def _update_user_skills_from_assessment(
        self,
        db: AsyncSession,
        user_id: int,
        skill_scores: Dict[int, float]
    ):
        """Update user skills based on assessment results."""
        for skill_id, score in skill_scores.items():
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
                    mastery_level=score,
                    confidence_score=0.7,  # High confidence from assessment
                    source="assessment"
                )
                db.add(user_skill)
            else:
                # Weighted average with existing mastery
                user_skill.mastery_level = user_skill.mastery_level * 0.3 + score * 0.7
                user_skill.confidence_score = min(1.0, user_skill.confidence_score + 0.1)
                user_skill.last_assessed = datetime.utcnow()
                user_skill.source = "assessment"
    
    async def generate_practice_questions(
        self,
        db: AsyncSession,
        skill_id: int,
        num_questions: int = 5,
        difficulty: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Generate practice questions for a specific skill.
        
        Args:
            db: Database session
            skill_id: Skill ID
            num_questions: Number of questions
            difficulty: Difficulty level (0-1)
        
        Returns:
            List of practice questions
        """
        # Get skill
        skill_result = await db.execute(
            select(Skill).where(Skill.id == skill_id)
        )
        skill = skill_result.scalar_one_or_none()
        
        if not skill:
            return []
        
        # Generate questions using AI
        questions = await ai_service.generate_questions(
            skill_name=skill.name,
            skill_description=skill.description or "",
            difficulty=difficulty,
            question_type="multiple_choice",
            num_questions=num_questions
        )
        
        return questions


# Singleton instance
assessment_service = AssessmentService()
