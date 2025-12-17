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

    def _normalize_phone(self, phone: Optional[str]) -> Optional[str]:
        if not phone:
            return None
        normalized = ''.join(filter(str.isdigit, phone))
        return normalized if normalized else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        if not email:
            return None
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user_from_phone(
        self,
        phone: Optional[str],
        email: str = None,
        name: str = None
    ) -> User:
        """
        Create a user account automatically after phone verification or for OAuth users.
        If phone is provided, username will be the normalized phone; otherwise a safe unique username
        will be generated (based on email or random).
        """
        normalized_phone = self._normalize_phone(phone)

        # If phone provided, check mobile uniqueness first
        if normalized_phone:
            existing_by_mobile = self.db.query(User).filter(User.mobile == normalized_phone).first()
            if existing_by_mobile:
                return existing_by_mobile

        # If email exists, try to reuse user by email
        if email:
            existing_by_email = self.get_user_by_email(email)
            if existing_by_email:
                # Ensure mobile saved if phone provided
                if normalized_phone and not existing_by_email.mobile:
                    existing_by_email.mobile = normalized_phone
                    self.db.flush()
                return existing_by_email

        # Generate base username
        if normalized_phone:
            base_username = normalized_phone
        elif email:
            base_username = email.split('@')[0]
        else:
            base_username = 'user'

        # Ensure username uniqueness by appending suffix if needed
        candidate = base_username
        suffix = 0
        while self.db.query(User).filter(User.username == candidate).first():
            suffix += 1
            candidate = f"{base_username}{suffix}"
            if suffix > 9999:
                # fallback to random
                candidate = f"{base_username}-{secrets.token_hex(4)}"
                break

        username_to_use = candidate

        # Generate secure random password for account (user can reset later)
        random_password = self.generate_secure_password()

        user = User(
            username=username_to_use,
            email=email or f"{username_to_use}@example.com",
            role='user',
            is_active=True
        )
        # write mobile and leave activation_code empty for now
        if normalized_phone:
            user.mobile = normalized_phone

        user.set_password(random_password)
        
        self.db.add(user)
        self.db.flush()
        
        return user
    
    def get_user_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number (mobile)"""
        normalized_phone = self._normalize_phone(phone)
        if not normalized_phone:
            return None
        return self.db.query(User).filter(User.mobile == normalized_phone).first()
    
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

