"""
Script to create an admin user
Run this once to set up your first admin account

Usage:
    python -m admin_area.create_admin
"""
from app.repositories.db import get_session, engine_factory
from admin_area.models import User, create_admin_user
from app.models.models import Base


def setup_database():
    """Create tables if they don't exist"""
    engine = engine_factory()
    Base.metadata.create_all(engine)
    print("Database tables created/verified.")


def create_admin():
    """Create an admin user"""
    import getpass
    
    print("=" * 50)
    print("Admin User Setup")
    print("=" * 50)
    
    username = input("Enter username: ").strip()
    if not username:
        print("Username cannot be empty!")
        return
    
    email = input("Enter email: ").strip()
    if not email:
        print("Email cannot be empty!")
        return
    
    password = getpass.getpass("Enter password: ")
    if len(password) < 6:
        print("Password must be at least 6 characters!")
        return
    
    # Bcrypt has a 72-byte limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        print("Warning: Password is longer than 72 bytes. It will be truncated.")
        print("Consider using a shorter password for better security.")
    
    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match!")
        return
    
    try:
        # Check if user already exists
        with next(get_session()) as db:
            existing = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing:
                print(f"User with username '{username}' or email '{email}' already exists!")
                return
            
            # Create admin user
            user = User(
                username=username,
                email=email,
                role='admin'
            )
            user.set_password(password)
            db.add(user)
            db.commit()
            
            print(f"\n✓ Admin user '{username}' created successfully!")
            print(f"  Email: {email}")
            print(f"  Role: admin")
    except Exception as e:
        print(f"Error creating admin user: {e}")


if __name__ == '__main__':
    setup_database()
    create_admin()

