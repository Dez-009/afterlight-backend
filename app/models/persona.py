from sqlalchemy import Column, String, DateTime, Text, Integer, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class PersonaAccessStatus(str, enum.Enum):
    ACTIVE = "active"
    LOCKED = "locked"
    GRACE_PERIOD = "grace_period"
    ARCHIVED = "archived"

class Persona(Base):
    """Persona model for AfterLight platform"""
    __tablename__ = "personas"
    
    # Core fields
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    relationship_type = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    date_of_passing = Column(DateTime, nullable=True)
    age_at_passing = Column(Integer, nullable=True)
    
    # Personal details
    hometown = Column(String(255), nullable=True)
    occupation = Column(String(255), nullable=True)
    education = Column(String(255), nullable=True)
    military_service = Column(String(255), nullable=True)
    
    # Cultural and religious
    cultural_background = Column(String(100), nullable=True)
    religious_affiliation = Column(String(100), nullable=True)
    cultural_traditions = Column(Text, nullable=True)  # JSON string
    
    # Personality and memories
    personality_traits = Column(Text, nullable=True)  # JSON string
    life_story = Column(Text, nullable=True)
    memorable_quotes = Column(Text, nullable=True)  # JSON string
    hobbies_interests = Column(Text, nullable=True)  # JSON string
    
    # Family and relationships
    family_members = Column(Text, nullable=True)  # JSON string
    close_friends = Column(Text, nullable=True)  # JSON string
    pets = Column(Text, nullable=True)  # JSON string
    
    # Memorial preferences
    memorial_type = Column(String(100), nullable=True)  # funeral, celebration, etc.
    venue_preferences = Column(Text, nullable=True)  # JSON string
    music_preferences = Column(Text, nullable=True)  # JSON string
    flower_preferences = Column(Text, nullable=True)  # JSON string
    
    # Media and files
    avatar_url = Column(String(500), nullable=True)
    avatar_updated_at = Column(DateTime(timezone=True), nullable=True)
    photos = Column(Text, nullable=True)  # JSON string of photo URLs
    videos = Column(Text, nullable=True)  # JSON string of video URLs
    documents = Column(Text, nullable=True)  # JSON string of document URLs
    
    # Access control and status
    access_status = Column(Enum(PersonaAccessStatus), default=PersonaAccessStatus.ACTIVE, nullable=False)
    locked_at = Column(DateTime(timezone=True), nullable=True)
    locked_reason = Column(String(500), nullable=True)
    priority_order = Column(Integer, default=0, nullable=False)
    
    # Storage and usage
    storage_used_mb = Column(Integer, default=0, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user_relation = relationship("User", back_populates="personas")
    memories = relationship("Memory", back_populates="persona", cascade="all, delete-orphan")
    media_files = relationship("Media", back_populates="persona", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Persona(id={self.id}, name={self.name}, status={self.access_status})>"
    
    @property
    def is_locked(self) -> bool:
        """Check if persona is locked"""
        return self.access_status in [PersonaAccessStatus.LOCKED, PersonaAccessStatus.GRACE_PERIOD]
    
    @property
    def can_be_accessed(self) -> bool:
        """Check if persona can be accessed by user"""
        return self.access_status == PersonaAccessStatus.ACTIVE
    
    @property
    def display_name(self) -> str:
        """Get display name with relationship"""
        if self.relationship_type:
            return f"{self.name} ({self.relationship_type})"
        return self.name
    
    def lock(self, reason: str = None):
        """Lock persona access"""
        self.access_status = PersonaAccessStatus.LOCKED
        self.locked_at = func.now()
        self.locked_reason = reason or "Subscription limit exceeded"
    
    def unlock(self):
        """Unlock persona access"""
        self.access_status = PersonaAccessStatus.ACTIVE
        self.locked_at = None
        self.locked_reason = None
    
    def set_grace_period(self, reason: str = None):
        """Set persona to grace period"""
        self.access_status = PersonaAccessStatus.GRACE_PERIOD
        self.locked_at = func.now()
        self.locked_reason = reason or "Grace period - upgrade required"
    
    def archive(self):
        """Archive persona"""
        self.access_status = PersonaAccessStatus.ARCHIVED
        self.locked_at = func.now()
        self.locked_reason = "Archived by user"
    
    def update_storage_usage(self, file_size_mb: int):
        """Update storage usage for this persona"""
        self.storage_used_mb += file_size_mb
    
    def get_cultural_traditions(self) -> dict:
        """Get cultural traditions as dictionary"""
        if not self.cultural_traditions:
            return {}
        try:
            import json
            return json.loads(self.cultural_traditions)
        except:
            return {}
    
    def set_cultural_traditions(self, traditions: dict):
        """Set cultural traditions from dictionary"""
        import json
        self.cultural_traditions = json.dumps(traditions)
    
    def get_personality_traits(self) -> list:
        """Get personality traits as list"""
        if not self.personality_traits:
            return []
        try:
            import json
            return json.loads(self.personality_traits)
        except:
            return []
    
    def set_personality_traits(self, traits: list):
        """Set personality traits from list"""
        import json
        self.personality_traits = json.dumps(traits)
    
    def get_memorable_quotes(self) -> list:
        """Get memorable quotes as list"""
        if not self.memorable_quotes:
            return []
        try:
            import json
            return json.loads(self.memorable_quotes)
        except:
            return []
    
    def set_memorable_quotes(self, quotes: list):
        """Set memorable quotes from list"""
        import json
        self.memorable_quotes = json.dumps(quotes)
    
    def get_hobbies_interests(self) -> list:
        """Get hobbies and interests as list"""
        if not self.hobbies_interests:
            return []
        try:
            import json
            return json.loads(self.hobbies_interests)
        except:
            return []
    
    def set_hobbies_interests(self, hobbies: list):
        """Set hobbies and interests from list"""
        import json
        self.hobbies_interests = json.dumps(hobbies)
    
    def get_family_members(self) -> list:
        """Get family members as list"""
        if not self.family_members:
            return []
        try:
            import json
            return json.loads(self.family_members)
        except:
            return []
    
    def set_family_members(self, members: list):
        """Set family members from list"""
        import json
        self.family_members = json.dumps(members)
    
    def get_close_friends(self) -> list:
        """Get close friends as list"""
        if not self.close_friends:
            return []
        try:
            import json
            return json.loads(self.close_friends)
        except:
            return []
    
    def set_close_friends(self, friends: list):
        """Set close friends from list"""
        import json
        self.close_friends = json.dumps(friends)
    
    def get_pets(self) -> list:
        """Get pets as list"""
        if not self.pets:
            return []
        try:
            import json
            return json.loads(self.pets)
        except:
            return []
    
    def set_pets(self, pets: list):
        """Set pets from list"""
        import json
        self.pets = json.dumps(pets)
    
    def get_venue_preferences(self) -> dict:
        """Get venue preferences as dictionary"""
        if not self.venue_preferences:
            return {}
        try:
            import json
            return json.loads(self.venue_preferences)
        except:
            return {}
    
    def set_venue_preferences(self, preferences: dict):
        """Set venue preferences from dictionary"""
        import json
        self.venue_preferences = json.dumps(preferences)
    
    def get_music_preferences(self) -> list:
        """Get music preferences as list"""
        if not self.music_preferences:
            return []
        try:
            import json
            return json.loads(self.music_preferences)
        except:
            return []
    
    def set_music_preferences(self, preferences: list):
        """Set music preferences from list"""
        import json
        self.music_preferences = json.dumps(preferences)
    
    def get_flower_preferences(self) -> list:
        """Get flower preferences as list"""
        if not self.flower_preferences:
            return []
        try:
            import json
            return json.loads(self.flower_preferences)
        except:
            return []
    
    def set_flower_preferences(self, preferences: list):
        """Set flower preferences from list"""
        import json
        self.flower_preferences = json.dumps(preferences)
    
    def get_photos(self) -> list:
        """Get photos as list"""
        if not self.photos:
            return []
        try:
            import json
            return json.loads(self.photos)
        except:
            return []
    
    def set_photos(self, photos: list):
        """Set photos from list"""
        import json
        self.photos = json.dumps(photos)
    
    def get_videos(self) -> list:
        """Get videos as list"""
        if not self.videos:
            return []
        try:
            import json
            return json.loads(self.videos)
        except:
            return []
    
    def set_videos(self, videos: list):
        """Set videos from list"""
        import json
        self.videos = json.dumps(videos)
    
    def get_documents(self) -> list:
        """Get documents as list"""
        if not self.documents:
            return []
        try:
            import json
            return json.loads(self.documents)
        except:
            return []
    
    def set_documents(self, documents: list):
        """Set documents from list"""
        import json
        self.documents = json.dumps(documents)
