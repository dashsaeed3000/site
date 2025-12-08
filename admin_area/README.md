# Admin Area Module

This module provides authentication and admin panel functionality using Flask-Login and Flask-Admin.

## Features

- **Authentication System**: Flask-Login based authentication with role-based access control
- **Admin Panel**: Flask-Admin interface for managing content
- **User Management**: User model with admin/user roles
- **Protected Routes**: Only admin users can access the admin panel

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask-Login (for authentication)
- Flask-Admin (for admin panel)
- passlib[bcrypt] (for password hashing)

### 2. Create Database Tables

The tables will be created automatically when you run migrations or use the setup script.

### 3. Create Admin User

Run the setup script to create your first admin user:

```bash
python -m admin_area.create_admin
```

Follow the prompts to enter:
- Username
- Email
- Password (minimum 6 characters)

## Usage

### Access Admin Panel

1. Navigate to `/admin/login`
2. Enter your admin credentials
3. You'll be redirected to `/admin` (Flask-Admin panel)

### Routes

- `/admin/login` - Login page
- `/admin/logout` - Logout (requires authentication)
- `/admin` - Admin panel (requires admin role)

### Models

- **User**: Authentication model with username, email, password, and role
- **Post**: Sample model for admin panel demonstration

### Creating Additional Admin Users

You can create admin users programmatically:

```python
from admin_area.models import create_admin_user

user = create_admin_user(
    username='admin2',
    email='admin2@example.com',
    password='secure_password'
)
```

## Configuration

The module uses placeholder values for:
- `SECRET_KEY`: Set in your `.env` file or `app/config/settings.py`
- Database configuration: Uses existing database settings from `app/config/settings.py`

## Security Notes

- Passwords are hashed using bcrypt
- Only users with `role='admin'` can access the admin panel
- All admin routes are protected with `@login_required`
- CSRF protection is enabled via Flask-WTF

## File Structure

```
admin_area/
├── __init__.py          # Module initialization
├── models.py            # User and Post models
├── forms.py             # LoginForm
├── routes.py            # Authentication routes
├── admin_views.py       # Flask-Admin views
├── create_admin.py      # Setup script
├── templates/
│   ├── login.html       # Login page
│   └── admin_base.html  # Admin base template
└── README.md            # This file
```

