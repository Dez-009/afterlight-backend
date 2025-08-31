from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    RELIGIOUS = "religious"
    HEALTHCARE = "healthcare"
    OTHER = "other"

class User(Base):
    """User model for AfterLight platform"""
    __tablename__ = "users"
    
    # Core fields
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    
    # Subscription and billing
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    subscription_expires_at = Column(DateTime, nullable=True)
    billing_email = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Cultural preferences
    cultural_background = Column(String(100), nullable=True)
    religious_affiliation = Column(String(100), nullable=True)
    language_preference = Column(String(10), default="en", nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    
    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    
    # Limits and usage
    max_personas = Column(Integer, default=1, nullable=False)
    max_storage_mb = Column(Integer, default=100, nullable=False)
    current_storage_mb = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    personas = relationship("Persona", back_populates="user_relation", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    planning_sessions = relationship("PlanningSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, tier={self.subscription_tier})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return self.email
    
    @property
    def is_subscription_active(self) -> bool:
        """Check if user has active subscription"""
        if not self.subscription_expires_at:
            return True  # No expiration means active
        return self.subscription_expires_at > func.now()
    
    @property
    def can_create_persona(self) -> bool:
        """Check if user can create more personas"""
        if not self.is_subscription_active:
            return False
        
        # Count active personas
        active_personas = sum(1 for p in self.personas if p.access_status == "active")
        return active_personas < self.max_personas
    
    @property
    def storage_usage_percentage(self) -> float:
        """Get storage usage as percentage"""
        if self.max_storage_mb == 0:
            return 0.0
        return (self.current_storage_mb / self.max_storage_mb) * 100
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.role == UserRole.SUPER_ADMIN:
            return True
        
        if self.role == UserRole.ADMIN and permission in ["manage_users", "manage_content", "view_analytics"]:
            return True
        
        # Check custom permissions
        if self.permissions:
            try:
                import json
                user_permissions = json.loads(self.permissions)
                return permission in user_permissions
            except:
                pass
        
        return False
    
    def upgrade_subscription(self, new_tier: SubscriptionTier, expires_at: DateTime = None):
        """Upgrade user subscription"""
        self.subscription_tier = new_tier
        if expires_at:
            self.subscription_expires_at = expires_at
        
        # Update limits based on tier
        tier_limits = {
            SubscriptionTier.FREE: {"personas": 1, "storage": 100},
            SubscriptionTier.PREMIUM: {"personas": 5, "storage": 1000},
            SubscriptionTier.RELIGIOUS: {"personas": 10, "storage": 2000},
            SubscriptionTier.HEALTHCARE: {"personas": 20, "storage": 5000},
            SubscriptionTier.OTHER: {"personas": 10, "storage": 2000}
        }
        
        limits = tier_limits.get(new_tier, {"personas": 1, "storage": 100})
        self.max_personas = limits["personas"]
        self.max_storage_mb = limits["storage"]
        self.is_premium = new_tier != SubscriptionTier.FREE
    
    def downgrade_subscription(self, new_tier: SubscriptionTier):
        """Downgrade user subscription"""
        old_tier = self.subscription_tier
        self.subscription_tier = new_tier
        
        # Update limits
        tier_limits = {
            SubscriptionTier.FREE: {"personas": 1, "storage": 100},
            SubscriptionTier.PREMIUM: {"personas": 5, "storage": 1000},
            SubscriptionTier.RELIGIOUS: {"personas": 10, "storage": 2000},
            SubscriptionTier.HEALTHCARE: {"personas": 20, "storage": 5000},
            SubscriptionTier.OTHER: {"personas": 10, "storage": 2000}
        }
        
        limits = tier_limits.get(new_tier, {"personas": 1, "storage": 100})
        self.max_personas = limits["personas"]
        self.max_storage_mb = limits["storage"]
        self.is_premium = new_tier != SubscriptionTier.FREE
        
        # Return old tier for downgrade processing
        return old_tier
