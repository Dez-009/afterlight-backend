from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.models.persona import Persona, PersonaAccessStatus
from app.models.user import User
from app.middleware.auth import get_current_user, require_subscription
from app.schemas.persona import (
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    PersonaListResponse,
    PersonaAccessUpdate
)

router = APIRouter()

@router.get("/", response_model=PersonaListResponse)
async def get_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[PersonaAccessStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all personas for the current user"""
    try:
        query = db.query(Persona).filter(Persona.user_id == current_user.id)
        
        # Filter by status if provided
        if status:
            query = query.filter(Persona.access_status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        personas = query.offset(skip).limit(limit).all()
        
        return PersonaListResponse(
            success=True,
            data=personas,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch personas: {str(e)}")

@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific persona by ID"""
    try:
        persona = db.query(Persona).filter(
            Persona.id == persona_id,
            Persona.user_id == current_user.id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        return PersonaResponse(
            success=True,
            data=persona
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch persona: {str(e)}")

@router.post("/", response_model=PersonaResponse)
async def create_persona(
    persona_data: PersonaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_subscription("free"))
):
    """Create a new persona"""
    try:
        # Check if user can create more personas
        if not current_user.can_create_persona:
            raise HTTPException(
                status_code=403,
                detail="Persona limit reached. Please upgrade your subscription."
            )
        
        # Create new persona
        persona = Persona(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            name=persona_data.name,
            relationship_type=persona_data.relationship_type,
            date_of_birth=persona_data.date_of_birth,
            date_of_passing=persona_data.date_of_passing,
            age_at_passing=persona_data.age_at_passing,
            hometown=persona_data.hometown,
            occupation=persona_data.occupation,
            education=persona_data.education,
            military_service=persona_data.military_service,
            cultural_background=persona_data.cultural_background,
            religious_affiliation=persona_data.religious_affiliation,
            cultural_traditions=persona_data.cultural_traditions,
            personality_traits=persona_data.personality_traits,
            life_story=persona_data.life_story,
            memorable_quotes=persona_data.memorable_quotes,
            hobbies_interests=persona_data.hobbies_interests,
            family_members=persona_data.family_members,
            close_friends=persona_data.close_friends,
            pets=persona_data.pets,
            memorial_type=persona_data.memorial_type,
            venue_preferences=persona_data.venue_preferences,
            music_preferences=persona_data.music_preferences,
            flower_preferences=persona_data.flower_preferences,
            priority_order=persona_data.priority_order or 0
        )
        
        db.add(persona)
        db.commit()
        db.refresh(persona)
        
        return PersonaResponse(
            success=True,
            data=persona,
            message="Persona created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create persona: {str(e)}")

@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: str,
    persona_data: PersonaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing persona"""
    try:
        persona = db.query(Persona).filter(
            Persona.id == persona_id,
            Persona.user_id == current_user.id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Check if persona can be modified
        if not persona.can_be_accessed:
            raise HTTPException(
                status_code=403,
                detail="Cannot modify locked or archived persona"
            )
        
        # Update fields
        update_data = persona_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(persona, field):
                setattr(persona, field, value)
        
        persona.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(persona)
        
        return PersonaResponse(
            success=True,
            data=persona,
            message="Persona updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update persona: {str(e)}")

@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a persona"""
    try:
        persona = db.query(Persona).filter(
            Persona.id == persona_id,
            Persona.user_id == current_user.id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Check if persona can be deleted
        if not persona.can_be_accessed:
            raise HTTPException(
                status_code=403,
                detail="Cannot delete locked or archived persona"
            )
        
        # Delete persona
        db.delete(persona)
        db.commit()
        
        return {
            "success": True,
            "message": "Persona deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete persona: {str(e)}")

@router.patch("/{persona_id}/access", response_model=PersonaResponse)
async def update_persona_access(
    persona_id: str,
    access_data: PersonaAccessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update persona access status"""
    try:
        persona = db.query(Persona).filter(
            Persona.id == persona_id,
            Persona.user_id == current_user.id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Update access status
        if access_data.access_status == PersonaAccessStatus.LOCKED:
            persona.lock(access_data.locked_reason)
        elif access_data.access_status == PersonaAccessStatus.GRACE_PERIOD:
            persona.set_grace_period(access_data.locked_reason)
        elif access_data.access_status == PersonaAccessStatus.ACTIVE:
            persona.unlock()
        elif access_data.access_status == PersonaAccessStatus.ARCHIVED:
            persona.archive()
        
        # Update priority if provided
        if access_data.priority_order is not None:
            persona.priority_order = access_data.priority_order
        
        db.commit()
        db.refresh(persona)
        
        return PersonaResponse(
            success=True,
            data=persona,
            message="Persona access updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update persona access: {str(e)}")

@router.get("/{persona_id}/memories")
async def get_persona_memories(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get memories for a specific persona"""
    try:
        persona = db.query(Persona).filter(
            Persona.id == persona_id,
            Persona.user_id == current_user.id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # TODO: Implement memory retrieval
        # For now, return empty list
        return {
            "success": True,
            "data": [],
            "message": "Memories feature coming soon"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch memories: {str(e)}")

@router.post("/{persona_id}/avatar")
async def upload_persona_avatar(
    persona_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload avatar for a persona"""
    try:
        persona = db.query(Persona).filter(
            Persona.id == persona_id,
            Persona.user_id == current_user.id
        ).first()
        
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # TODO: Implement avatar upload
        # For now, return placeholder
        return {
            "success": True,
            "message": "Avatar upload feature coming soon"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")
