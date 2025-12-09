"""
Admin Area Module
Handles authentication and admin panel using Flask-Login and Flask-Admin
"""
from flask import Flask, redirect
from flask_login import LoginManager
from flask_admin import Admin

from .routes import admin_area_bp
from .admin_views import (
    AdminIndexView,
    PostModelView,
    CategoryAdminView,
    ProductAdminView,
    SecureModelView,
    SiteContentAdminView,
    BlogAdminView,
    BlogCategoryAdminView,
)


login_manager = LoginManager()
# Admin defaults to Bootstrap4Theme, so no need to specify theme
admin = Admin(
    name='پنل مدیریت',
    url='/admin',
)


def init_admin_area(app: Flask):
    """Initialize admin area with Flask-Login and Flask-Admin."""

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'admin_area.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'info'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models import get_user_by_id
        return get_user_by_id(user_id)

    # Add Persian date filter to admin templates
    from app.utils.persian_date import to_persian_date
    app.jinja_env.filters['persian_date'] = to_persian_date

    # Initialize Flask-Admin
    admin.init_app(app, index_view=AdminIndexView(name='Home', url='/admin'))

    # Register admin views
    from .models import Post
    from app.models.models import Categories, Products, BlogCategories, Blogs, SiteContent
    from app.repositories.db import get_scoped_session

    # Use a scoped session so Flask-Admin can call .query on it
    Session = get_scoped_session()

    # === MAIN SITE TABLES ONLY (product groups, products, blog) ===

    # Product groups / categories
    admin.add_view(CategoryAdminView(Categories, Session, name='دسته‌بندی‌ها'))

    # Products
    admin.add_view(ProductAdminView(Products, Session, name='محصولات'))

    # Blog categories and posts
    admin.add_view(BlogCategoryAdminView(BlogCategories, Session, name='دسته‌بندی مقالات'))
    admin.add_view(BlogAdminView(Blogs, Session, name='مقالات'))

    # Site content management
    admin.add_view(SiteContentAdminView(SiteContent, Session, name='محتوای سایت'))

    # Sample Post model from admin_area (you can remove this if not needed)
    admin.add_view(PostModelView(Post, Session, name='Posts', endpoint='posts'))

    # Register blueprint
    app.register_blueprint(admin_area_bp, url_prefix='/admin')

    # Ensure requests to `/admin` (no trailing slash) redirect to the admin index `/admin/`.
    # This avoids cases where the server doesn't automatically add a trailing slash
    # and the Flask-Admin index view is not reached.
    @app.route('/admin')
    def _admin_root_redirect():
        return redirect('/admin/')

    return app

