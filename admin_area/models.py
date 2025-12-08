"""
Admin Area Models
User model with role-based authentication
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
import enum
import bcrypt

from app.repositories.db import get_session
from app.models.models import Base


class UserRole(enum.Enum):
    ADMIN = 'admin'
    USER = 'user'


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='user')
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password: str):
        """Hash and set password using bcrypt directly"""
        # Bcrypt has a 72-byte limit, ensure password is within limit
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                # Truncate to 72 bytes (bcrypt limit)
                password_bytes = password_bytes[:72]
        else:
            password_bytes = password
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
        
        # Hash password using bcrypt directly
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password using bcrypt directly"""
        try:
            # Bcrypt has a 72-byte limit, truncate if necessary
            if isinstance(password, str):
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
            else:
                password_bytes = password
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
            
            # Verify password
            stored_hash = self.password_hash.encode('utf-8') if isinstance(self.password_hash, str) else self.password_hash
            return bcrypt.checkpw(password_bytes, stored_hash)
        except Exception as e:
            return False
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == 'admin'
    
    # Flask-Login required methods
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_active_prop(self):
        """Flask-Login compatibility"""
        return self.is_active


class Post(Base):
    """Sample Post model for admin panel"""
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=True)
    excerpt = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Post {self.title}>'


# Helper functions
def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        with next(get_session()) as db:
            return db.query(User).filter(User.id == int(user_id)).first()
    except (ValueError, TypeError):
        return None


def get_user_by_username(username: str):
    """Get user by username"""
    with next(get_session()) as db:
        return db.query(User).filter(User.username == username).first()


def create_admin_user(username: str, email: str, password: str):
    """Create an admin user (for initial setup)"""
    with next(get_session()) as db:
        user = User(
            username=username,
            email=email,
            role='admin'
        )
        user.set_password(password)
        db.add(user)
        db.commit()
        return user

