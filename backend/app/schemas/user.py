"""
User schemas for API validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    years_of_experience: Optional[int] = 0
    interests: Optional[List[str]] = []


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    years_of_experience: Optional[int] = None
    interests: Optional[List[str]] = None
    academic_background: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    bio: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    years_of_experience: int = 0
    interests: List[str] = []
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh."""
    refresh_token: str


class ResumeUploadResponse(BaseModel):
    """Schema for resume upload response."""
    message: str
    extracted_skills: List[Dict[str, Any]]
    education: Optional[Dict[str, Any]] = None
    experience: Optional[List[Dict[str, Any]]] = None
