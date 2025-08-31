from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.persona import PersonaAccessStatus

class PersonaBase(BaseModel):
    """Base persona schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Persona name")
    relationship_type: Optional[str] = Field(None, max_length=100, description="Relationship to user")
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    date_of_passing: Optional[datetime] = Field(None, description="Date of passing")
    age_at_passing: Optional[int] = Field(None, ge=0, le=150, description="Age at passing")
    
    hometown: Optional[str] = Field(None, max_length=255, description="Hometown")
    occupation: Optional[str] = Field(None, max_length=255, description="Occupation")
    education: Optional[str] = Field(None, max_length=255, description="Education")
    military_service: Optional[str] = Field(None, max_length=255, description="Military service")
    
    cultural_background: Optional[str] = Field(None, max_length=100, description="Cultural background")
    religious_affiliation: Optional[str] = Field(None, max_length=100, description="Religious affiliation")
    cultural_traditions: Optional[Dict[str, Any]] = Field(None, description="Cultural traditions")
    
    personality_traits: Optional[List[str]] = Field(None, description="Personality traits")
    life_story: Optional[str] = Field(None, description="Life story")
    memorable_quotes: Optional[List[str]] = Field(None, description="Memorable quotes")
    hobbies_interests: Optional[List[str]] = Field(None, description="Hobbies and interests")
    
    family_members: Optional[List[Dict[str, str]]] = Field(None, description="Family members")
    close_friends: Optional[List[Dict[str, str]]] = Field(None, description="Close friends")
    pets: Optional[List[Dict[str, str]]] = Field(None, description="Pets")
    
    memorial_type: Optional[str] = Field(None, max_length=100, description="Memorial type")
    venue_preferences: Optional[Dict[str, Any]] = Field(None, description="Venue preferences")
    music_preferences: Optional[List[str]] = Field(None, description="Music preferences")
    flower_preferences: Optional[List[str]] = Field(None, description="Flower preferences")
    
    priority_order: Optional[int] = Field(0, ge=0, description="Priority order for display")

class PersonaCreate(PersonaBase):
    """Schema for creating a new persona"""
    pass

class PersonaUpdate(BaseModel):
    """Schema for updating a persona"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    relationship_type: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[datetime] = None
    date_of_passing: Optional[datetime] = None
    age_at_passing: Optional[int] = Field(None, ge=0, le=150)
    
    hometown: Optional[str] = Field(None, max_length=255)
    occupation: Optional[str] = Field(None, max_length=255)
    education: Optional[str] = Field(None, max_length=255)
    military_service: Optional[str] = Field(None, max_length=255)
    
    cultural_background: Optional[str] = Field(None, max_length=100)
    religious_affiliation: Optional[str] = Field(None, max_length=100)
    cultural_traditions: Optional[Dict[str, Any]] = None
    
    personality_traits: Optional[List[str]] = None
    life_story: Optional[str] = None
    memorable_quotes: Optional[List[str]] = None
    hobbies_interests: Optional[List[str]] = None
    
    family_members: Optional[List[Dict[str, str]]] = None
    close_friends: Optional[List[Dict[str, str]]] = None
    pets: Optional[List[Dict[str, str]]] = None
    
    memorial_type: Optional[str] = Field(None, max_length=100)
    venue_preferences: Optional[Dict[str, Any]] = None
    music_preferences: Optional[List[str]] = None
    flower_preferences: Optional[List[str]] = None
    
    priority_order: Optional[int] = Field(None, ge=0)

class PersonaAccessUpdate(BaseModel):
    """Schema for updating persona access status"""
    access_status: PersonaAccessStatus
    locked_reason: Optional[str] = Field(None, max_length=500)
    priority_order: Optional[int] = Field(None, ge=0)

class PersonaResponse(BaseModel):
    """Schema for persona response"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None

class PersonaListResponse(BaseModel):
    """Schema for persona list response"""
    success: bool
    data: List[Any]
    total: int
    skip: int
    limit: int
    message: Optional[str] = None
    error: Optional[str] = None

# Avatar schemas
class AvatarUpload(BaseModel):
    """Schema for avatar upload"""
    file: Any  # Will be validated as file upload
    crop_x: Optional[int] = Field(None, ge=0)
    crop_y: Optional[int] = Field(None, ge=0)
    crop_width: Optional[int] = Field(None, ge=1)
    crop_height: Optional[int] = Field(None, ge=1)

class AvatarResponse(BaseModel):
    """Schema for avatar response"""
    success: bool
    avatar_url: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

# Memory schemas
class MemoryBase(BaseModel):
    """Base memory schema"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    memory_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    is_private: bool = False

class MemoryCreate(MemoryBase):
    """Schema for creating a memory"""
    pass

class MemoryUpdate(BaseModel):
    """Schema for updating a memory"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    memory_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None

class MemoryResponse(BaseModel):
    """Schema for memory response"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None

# Validation methods
@validator('personality_traits')
def validate_personality_traits(cls, v):
    """Validate personality traits list"""
    if v is not None:
        if len(v) > 20:
            raise ValueError('Personality traits cannot exceed 20 items')
        for trait in v:
            if len(trait) > 100:
                raise ValueError('Individual personality trait cannot exceed 100 characters')
    return v

@validator('memorable_quotes')
def validate_memorable_quotes(cls, v):
    """Validate memorable quotes list"""
    if v is not None:
        if len(v) > 50:
            raise ValueError('Memorable quotes cannot exceed 50 items')
        for quote in v:
            if len(quote) > 500:
                raise ValueError('Individual quote cannot exceed 500 characters')
    return v

@validator('hobbies_interests')
def validate_hobbies_interests(cls, v):
    """Validate hobbies and interests list"""
    if v is not None:
        if len(v) > 30:
            raise ValueError('Hobbies and interests cannot exceed 30 items')
        for hobby in v:
            if len(hobby) > 100:
                raise ValueError('Individual hobby cannot exceed 100 characters')
    return v

@validator('family_members', 'close_friends', 'pets')
def validate_relationship_lists(cls, v):
    """Validate relationship lists"""
    if v is not None:
        if len(v) > 100:
            raise ValueError('Relationship list cannot exceed 100 items')
        for item in v:
            if not isinstance(item, dict):
                raise ValueError('Relationship items must be dictionaries')
            if 'name' not in item:
                raise ValueError('Relationship items must have a name field')
    return v

@validator('music_preferences', 'flower_preferences')
def validate_preference_lists(cls, v):
    """Validate preference lists"""
    if v is not None:
        if len(v) > 50:
            raise ValueError('Preference list cannot exceed 50 items')
        for item in v:
            if len(item) > 100:
                raise ValueError('Individual preference cannot exceed 100 characters')
    return v
