# API Routes
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.skills import router as skills_router
from app.api.assessments import router as assessments_router
from app.api.learning import router as learning_router
from app.api.careers import router as careers_router
from app.api.digital_twin import router as digital_twin_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(skills_router, prefix="/skills", tags=["Skills"])
router.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
router.include_router(learning_router, prefix="/learning", tags=["Learning"])
router.include_router(careers_router, prefix="/careers", tags=["Careers"])
router.include_router(digital_twin_router, prefix="/digital-twin", tags=["Digital Twin"])
