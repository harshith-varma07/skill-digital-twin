"""
User API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, ResumeUploadResponse
from app.services.skill_extraction import skill_extraction_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse resume to extract skills."""
    # Validate file type
    allowed_types = [".pdf", ".docx", ".doc", ".txt"]
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {allowed_types}"
        )
    
    # Read file content
    content = await file.read()
    
    # Parse based on file type
    if file_ext == ".txt":
        text = content.decode("utf-8")
    elif file_ext == ".pdf":
        import pdfplumber
        import io
        
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    elif file_ext in [".docx", ".doc"]:
        from docx import Document
        import io
        
        doc = Document(io.BytesIO(content))
        text = "\n".join(para.text for para in doc.paragraphs)
    else:
        text = ""
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from file"
        )
    
    # Store resume text
    current_user.resume_text = text
    
    # Extract skills
    extracted_skills = await skill_extraction_service.extract_skills(
        text=text,
        context="resume",
        use_ai=True
    )
    
    await db.commit()
    
    return ResumeUploadResponse(
        message="Resume processed successfully",
        extracted_skills=extracted_skills,
        education=None,  # Could add education extraction
        experience=None  # Could add experience extraction
    )


@router.post("/me/interests")
async def update_interests(
    interests: list[str],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's interests."""
    current_user.interests = interests
    await db.commit()
    
    return {"message": "Interests updated", "interests": interests}


@router.get("/me/profile-completeness")
async def get_profile_completeness(current_user: User = Depends(get_current_user)):
    """Get profile completeness percentage."""
    completeness = 0
    
    if current_user.full_name:
        completeness += 15
    if current_user.bio:
        completeness += 10
    if current_user.education_level:
        completeness += 10
    if current_user.field_of_study:
        completeness += 10
    if current_user.interests:
        completeness += 10
    if current_user.resume_text:
        completeness += 25
    if current_user.academic_background:
        completeness += 10
    if current_user.years_of_experience > 0:
        completeness += 10
    
    return {
        "completeness_percentage": min(completeness, 100),
        "missing_fields": [
            field for field, has_value in [
                ("bio", current_user.bio),
                ("education_level", current_user.education_level),
                ("field_of_study", current_user.field_of_study),
                ("interests", current_user.interests),
                ("resume", current_user.resume_text),
                ("academic_background", current_user.academic_background)
            ] if not has_value
        ]
    }
