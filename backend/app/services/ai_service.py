"""
AI Service for OpenAI/LLM interactions.
"""
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import httpx

from app.core.config import settings


class AIService:
    """Service for AI-powered features using OpenAI."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """Generate a completion using the AI model."""
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def extract_skills_from_text(self, text: str, context: str = "general") -> List[Dict[str, Any]]:
        """Extract skills from text using AI."""
        system_message = """You are an expert skill extraction system. 
        Extract all technical and soft skills from the given text.
        Return a JSON array of skills with the following structure:
        [
            {
                "name": "skill name",
                "category": "technical/soft/domain",
                "confidence": 0.0-1.0,
                "evidence": "text snippet that indicates this skill",
                "proficiency_hint": "beginner/intermediate/advanced/expert"
            }
        ]
        Only return the JSON array, no other text."""
        
        prompt = f"""Context: {context}
        
        Text to analyze:
        {text}
        
        Extract all identifiable skills from this text."""
        
        response = await self.generate_completion(prompt, system_message, temperature=0.3)
        
        try:
            # Clean up the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            skills = json.loads(response)
            return skills
        except json.JSONDecodeError:
            return []
    
    async def generate_questions(
        self,
        skill_name: str,
        skill_description: str,
        difficulty: float,
        question_type: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate assessment questions for a skill."""
        difficulty_label = "easy" if difficulty < 0.33 else "medium" if difficulty < 0.66 else "hard"
        
        system_message = """You are an expert educational assessment creator.
        Generate high-quality questions to assess skill proficiency.
        Return a JSON array with the following structure:
        [
            {
                "question_text": "the question",
                "question_type": "multiple_choice/true_false/short_answer/coding",
                "options": ["A", "B", "C", "D"],  // for multiple choice
                "correct_answer": "the correct answer or option letter",
                "explanation": "why this is correct",
                "difficulty": 0.0-1.0
            }
        ]
        Only return the JSON array, no other text."""
        
        prompt = f"""Generate {num_questions} {difficulty_label} {question_type} questions to assess proficiency in:
        
        Skill: {skill_name}
        Description: {skill_description}
        
        Questions should progressively test understanding from basic concepts to application."""
        
        response = await self.generate_completion(prompt, system_message, temperature=0.5)
        
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            questions = json.loads(response)
            return questions
        except json.JSONDecodeError:
            return []
    
    async def generate_topic_overview(self, skill_name: str, context: str = "") -> Dict[str, Any]:
        """Generate a comprehensive topic overview for learning."""
        system_message = """You are an expert educational content creator.
        Generate comprehensive learning content for a topic.
        Return a JSON object with:
        {
            "overview": "detailed topic overview (2-3 paragraphs)",
            "key_concepts": ["concept1", "concept2", ...],
            "learning_objectives": ["objective1", "objective2", ...],
            "prerequisites": ["prerequisite1", ...],
            "difficulty_level": "beginner/intermediate/advanced",
            "estimated_hours": 5.0,
            "subtopics": [
                {"name": "subtopic", "description": "brief description"}
            ]
        }
        Only return the JSON object, no other text."""
        
        prompt = f"""Create a comprehensive learning overview for:
        
        Topic/Skill: {skill_name}
        {f"Additional context: {context}" if context else ""}
        
        Include practical applications and real-world relevance."""
        
        response = await self.generate_completion(prompt, system_message, temperature=0.5)
        
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "overview": f"Learn about {skill_name}",
                "key_concepts": [],
                "learning_objectives": [],
                "prerequisites": [],
                "difficulty_level": "intermediate",
                "estimated_hours": 10.0,
                "subtopics": []
            }
    
    async def generate_learning_roadmap(
        self,
        skill_gaps: List[Dict[str, Any]],
        current_skills: List[Dict[str, Any]],
        target_role: Optional[str] = None,
        learning_style: str = "mixed"
    ) -> Dict[str, Any]:
        """Generate a personalized learning roadmap."""
        system_message = """You are an expert learning path designer.
        Create an optimal learning roadmap to address skill gaps.
        Return a JSON object with:
        {
            "title": "roadmap title",
            "description": "roadmap description",
            "total_estimated_hours": 50.0,
            "modules": [
                {
                    "title": "module title",
                    "description": "module description",
                    "skills_addressed": ["skill1", "skill2"],
                    "estimated_hours": 10.0,
                    "order": 1,
                    "topics": ["topic1", "topic2"],
                    "search_keywords": ["youtube search term 1", "youtube search term 2"]
                }
            ],
            "milestones": [
                {"name": "milestone", "after_module": 2, "description": "what you'll achieve"}
            ]
        }
        Only return the JSON object, no other text."""
        
        gaps_text = "\n".join([
            f"- {g.get('skill_name', 'Unknown')}: Current {g.get('current_level', 0):.0%}, Need {g.get('required_level', 0):.0%}"
            for g in skill_gaps
        ])
        
        current_text = "\n".join([
            f"- {s.get('skill_name', 'Unknown')}: {s.get('mastery_level', 0):.0%}"
            for s in current_skills[:10]
        ])
        
        prompt = f"""Create a personalized learning roadmap:
        
        Target Role: {target_role or 'General skill development'}
        Learning Style Preference: {learning_style}
        
        Current Skills:
        {current_text}
        
        Skill Gaps to Address:
        {gaps_text}
        
        Create an efficient, logical learning path with modules ordered by prerequisites and importance."""
        
        response = await self.generate_completion(prompt, system_message, max_tokens=3000, temperature=0.5)
        
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "title": "Learning Roadmap",
                "description": "Personalized learning path",
                "total_estimated_hours": 0,
                "modules": [],
                "milestones": []
            }
    
    async def evaluate_response(
        self,
        question: str,
        user_response: str,
        correct_answer: str,
        skill_context: str
    ) -> Dict[str, Any]:
        """Evaluate a user's response to an open-ended question."""
        system_message = """You are an expert educational evaluator.
        Evaluate the student's response and provide feedback.
        Return a JSON object with:
        {
            "is_correct": true/false,
            "score": 0.0-1.0,
            "feedback": "detailed feedback",
            "strengths": ["what they got right"],
            "improvements": ["what could be better"],
            "partial_credit_breakdown": {"concept1": 0.5, "concept2": 1.0}
        }
        Only return the JSON object, no other text."""
        
        prompt = f"""Evaluate this response:
        
        Skill/Topic: {skill_context}
        
        Question: {question}
        
        Expected Answer: {correct_answer}
        
        Student's Response: {user_response}
        
        Provide fair, constructive evaluation."""
        
        response = await self.generate_completion(prompt, system_message, temperature=0.3)
        
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": "Unable to evaluate response",
                "strengths": [],
                "improvements": []
            }
    
    async def analyze_career_fit(
        self,
        user_skills: List[Dict[str, Any]],
        career_role: Dict[str, Any],
        required_skills: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze how well a user fits a career role."""
        system_message = """You are an expert career advisor.
        Analyze the fit between a candidate's skills and a job role.
        Return a JSON object with:
        {
            "overall_fit_score": 0.0-1.0,
            "strengths": ["strength1", "strength2"],
            "gaps": ["gap1", "gap2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "time_to_ready_weeks": 12,
            "priority_actions": ["action1", "action2"],
            "confidence_level": 0.0-1.0
        }
        Only return the JSON object, no other text."""
        
        user_skills_text = "\n".join([
            f"- {s.get('skill_name', 'Unknown')}: {s.get('mastery_level', 0):.0%}"
            for s in user_skills
        ])
        
        required_text = "\n".join([
            f"- {s.get('skill_name', 'Unknown')}: {s.get('required_level', 0):.0%} (importance: {s.get('importance', 0.5):.0%})"
            for s in required_skills
        ])
        
        prompt = f"""Analyze career fit:
        
        Role: {career_role.get('title', 'Unknown')}
        Description: {career_role.get('description', '')}
        
        Candidate's Skills:
        {user_skills_text}
        
        Required Skills:
        {required_text}
        
        Provide actionable analysis."""
        
        response = await self.generate_completion(prompt, system_message, temperature=0.4)
        
        try:
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "overall_fit_score": 0.0,
                "strengths": [],
                "gaps": [],
                "recommendations": [],
                "time_to_ready_weeks": 0,
                "priority_actions": [],
                "confidence_level": 0.5
            }


# Singleton instance
ai_service = AIService()
