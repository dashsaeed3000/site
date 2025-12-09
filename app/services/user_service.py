"""
User Service
Business logic for user operations
"""
from typing import Optional
from sqlalchemy.orm import Session
from admin_area.models import User, get_user_by_username, get_user_by_id
from app.repositories.db import get_session
import secrets
import string


class UserService:
    """Service for user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def create_user_from_phone(
        self,
        phone: str,
        email: str = None,
        name: str = None
    ) -> User:
        """
        Create a user account automatically after phone verification.
        Uses phone number as username.
        """
        # Normalize phone number
        normalized_phone = ''.join(filter(str.isdigit, phone))
        
        # Check if user already exists
        existing_user = get_user_by_username(normalized_phone)
        if existing_user:
            return existing_user
        
        # Generate secure random password
        random_password = self.generate_secure_password()
        
        # Create user
        user = User(
            username=normalized_phone,
            email=email or f"{normalized_phone}@example.com",  # Placeholder email
            role='user',
            is_active=True
        )
        user.set_password(random_password)
        
        self.db.add(user)
        self.db.flush()
        
        return user
    
    def get_user_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number (username)"""
        normalized_phone = ''.join(filter(str.isdigit, phone))
        return get_user_by_username(normalized_phone)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return get_user_by_id(user_id)
    
    def update_user_email(self, user_id: int, email: str) -> Optional[User]:
        """Update user email"""
        user = self.get_user_by_id(user_id)
        if user:
            user.email = email
            self.db.flush()
        return user

