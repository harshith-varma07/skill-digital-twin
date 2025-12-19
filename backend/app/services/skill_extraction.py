"""
Skill Extraction Service using NLP techniques.
"""
import re
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict

from app.services.ai_service import ai_service


class SkillExtractionService:
    """Service for extracting skills from text using NLP."""
    
    def __init__(self):
        # Common skill patterns and keywords
        self.technical_skills = {
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
            "swift", "kotlin", "php", "scala", "r", "matlab", "perl", "shell", "bash",
            
            # Web Technologies
            "html", "css", "react", "angular", "vue", "node.js", "express", "django",
            "flask", "fastapi", "spring", "asp.net", "rails", "laravel", "nextjs",
            
            # Data & ML
            "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
            "scikit-learn", "pandas", "numpy", "data analysis", "data science",
            "natural language processing", "nlp", "computer vision", "ai",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "cassandra", "dynamodb", "oracle", "sqlite", "neo4j",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
            "jenkins", "ci/cd", "devops", "linux", "git", "github", "gitlab",
            
            # Other Technical
            "api", "rest", "graphql", "microservices", "agile", "scrum",
            "testing", "unit testing", "automation", "security", "networking"
        }
        
        self.soft_skills = {
            "communication", "leadership", "teamwork", "problem solving",
            "critical thinking", "time management", "project management",
            "collaboration", "adaptability", "creativity", "negotiation",
            "presentation", "public speaking", "mentoring", "decision making",
            "conflict resolution", "emotional intelligence", "organization"
        }
        
        # Skill category mapping
        self.category_mapping = {
            "programming": ["python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "swift", "kotlin", "php", "scala", "r"],
            "web_development": ["html", "css", "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "nextjs"],
            "data_science": ["machine learning", "deep learning", "data analysis", "data science", "pandas", "numpy", "tensorflow", "pytorch"],
            "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform"],
            "devops": ["ci/cd", "devops", "jenkins", "ansible", "git"],
            "soft_skills": list(self.soft_skills)
        }
    
    async def extract_skills(
        self,
        text: str,
        context: str = "general",
        use_ai: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract skills from text using pattern matching and AI.
        
        Args:
            text: The text to extract skills from
            context: Context hint ('resume', 'academic', 'self_description')
            use_ai: Whether to use AI for enhanced extraction
        
        Returns:
            List of extracted skills with metadata
        """
        extracted_skills = []
        found_skills: Set[str] = set()
        text_lower = text.lower()
        
        # Pattern-based extraction
        pattern_skills = self._pattern_based_extraction(text_lower)
        for skill_info in pattern_skills:
            if skill_info["name"] not in found_skills:
                found_skills.add(skill_info["name"])
                extracted_skills.append(skill_info)
        
        # AI-powered extraction for more nuanced skills
        if use_ai:
            ai_skills = await ai_service.extract_skills_from_text(text, context)
            for skill_info in ai_skills:
                skill_name = skill_info.get("name", "").lower()
                if skill_name and skill_name not in found_skills:
                    found_skills.add(skill_name)
                    extracted_skills.append({
                        "name": skill_info.get("name", ""),
                        "category": skill_info.get("category", "unknown"),
                        "confidence": skill_info.get("confidence", 0.7),
                        "evidence": skill_info.get("evidence", ""),
                        "proficiency_hint": skill_info.get("proficiency_hint", "intermediate"),
                        "source": "ai"
                    })
        
        # Sort by confidence
        extracted_skills.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return extracted_skills
    
    def _pattern_based_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills using pattern matching."""
        extracted = []
        
        # Check technical skills
        for skill in self.technical_skills:
            if self._skill_present(skill, text):
                category = self._get_category(skill)
                confidence = self._calculate_confidence(skill, text)
                extracted.append({
                    "name": skill,
                    "category": category,
                    "confidence": confidence,
                    "evidence": self._get_evidence(skill, text),
                    "proficiency_hint": self._estimate_proficiency(skill, text),
                    "source": "pattern"
                })
        
        # Check soft skills
        for skill in self.soft_skills:
            if self._skill_present(skill, text):
                confidence = self._calculate_confidence(skill, text)
                extracted.append({
                    "name": skill,
                    "category": "soft_skills",
                    "confidence": confidence,
                    "evidence": self._get_evidence(skill, text),
                    "proficiency_hint": "intermediate",
                    "source": "pattern"
                })
        
        return extracted
    
    def _skill_present(self, skill: str, text: str) -> bool:
        """Check if a skill is present in the text."""
        # Word boundary matching
        pattern = r'\b' + re.escape(skill) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
    
    def _get_category(self, skill: str) -> str:
        """Get the category of a skill."""
        skill_lower = skill.lower()
        for category, skills in self.category_mapping.items():
            if skill_lower in [s.lower() for s in skills]:
                return category
        return "technical"
    
    def _calculate_confidence(self, skill: str, text: str) -> float:
        """Calculate confidence score based on context."""
        confidence = 0.5
        
        # Higher confidence if skill appears multiple times
        count = len(re.findall(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE))
        if count > 1:
            confidence += min(count * 0.1, 0.3)
        
        # Higher confidence if near experience indicators
        experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience\s*(?:in|with))?\s*' + re.escape(skill),
            r'experienced\s+(?:in\s+)?' + re.escape(skill),
            r'expert\s+(?:in\s+)?' + re.escape(skill),
            r'proficient\s+(?:in\s+)?' + re.escape(skill),
        ]
        
        for pattern in experience_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                confidence += 0.15
                break
        
        return min(confidence, 1.0)
    
    def _get_evidence(self, skill: str, text: str, context_chars: int = 100) -> str:
        """Get text evidence for the skill."""
        pattern = r'\b' + re.escape(skill) + r'\b'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            start = max(0, match.start() - context_chars // 2)
            end = min(len(text), match.end() + context_chars // 2)
            return "..." + text[start:end] + "..."
        
        return ""
    
    def _estimate_proficiency(self, skill: str, text: str) -> str:
        """Estimate proficiency level from context."""
        skill_pattern = re.escape(skill)
        
        expert_patterns = [
            r'expert\s+(?:in\s+)?' + skill_pattern,
            r'(\d+)\s*\+?\s*years?\s*(?:of\s*)?(?:experience\s*(?:in|with))?\s*' + skill_pattern,
            r'advanced\s+' + skill_pattern,
            r'senior\s+' + skill_pattern,
        ]
        
        intermediate_patterns = [
            r'proficient\s+(?:in\s+)?' + skill_pattern,
            r'experienced\s+(?:in\s+)?' + skill_pattern,
            r'working\s+knowledge\s+(?:of\s+)?' + skill_pattern,
        ]
        
        for pattern in expert_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "advanced"
        
        for pattern in intermediate_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "intermediate"
        
        return "beginner"
    
    def categorize_skills(
        self,
        skills: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Organize skills by category."""
        categorized = defaultdict(list)
        
        for skill in skills:
            category = skill.get("category", "other")
            categorized[category].append(skill)
        
        return dict(categorized)
    
    async def map_to_ontology(
        self,
        extracted_skills: List[Dict[str, Any]],
        ontology_skills: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Map extracted skills to the skill ontology.
        
        Args:
            extracted_skills: Skills extracted from text
            ontology_skills: Skills defined in the system ontology
        
        Returns:
            List of matched skills with ontology IDs
        """
        mapped_skills = []
        ontology_lookup = {s["name"].lower(): s for s in ontology_skills}
        
        for skill in extracted_skills:
            skill_name = skill["name"].lower()
            
            # Direct match
            if skill_name in ontology_lookup:
                ontology_skill = ontology_lookup[skill_name]
                mapped_skills.append({
                    **skill,
                    "ontology_id": ontology_skill.get("id"),
                    "ontology_name": ontology_skill.get("name"),
                    "match_type": "exact"
                })
            else:
                # Try fuzzy matching with keywords
                for ont_skill in ontology_skills:
                    keywords = ont_skill.get("keywords", [])
                    if skill_name in [k.lower() for k in keywords]:
                        mapped_skills.append({
                            **skill,
                            "ontology_id": ont_skill.get("id"),
                            "ontology_name": ont_skill.get("name"),
                            "match_type": "keyword"
                        })
                        break
                else:
                    # No match found, mark as new skill candidate
                    mapped_skills.append({
                        **skill,
                        "ontology_id": None,
                        "ontology_name": None,
                        "match_type": "unmapped"
                    })
        
        return mapped_skills


# Singleton instance
skill_extraction_service = SkillExtractionService()
