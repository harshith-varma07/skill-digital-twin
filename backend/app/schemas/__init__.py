# Pydantic schemas
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, Token
from app.schemas.skill import SkillCreate, SkillResponse, UserSkillCreate, UserSkillResponse, SkillCategoryResponse
from app.schemas.assessment import (
    AssessmentCreate, AssessmentResponse, QuestionCreate, QuestionResponse,
    AssessmentResponseCreate, DiagnosticRequest
)
from app.schemas.learning import (
    LearningRoadmapCreate, LearningRoadmapResponse, LearningModuleResponse,
    LearningResourceResponse, RoadmapGenerationRequest
)
from app.schemas.career import (
    CareerRoleCreate, CareerRoleResponse, CareerAlignmentResponse,
    CareerAnalysisRequest
)
from app.schemas.digital_twin import SkillDigitalTwinResponse, GapAnalysisResponse
