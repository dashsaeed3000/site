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
        UserAdminView,
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

    # Simple UI translations for Flask-Admin strings used in templates.
    # This is a lightweight fallback mapping (no Flask-Babel required).
    def _translate(s):
        mapping = {
            'Create': 'ایجاد',
            'Edit': 'ویرایش',
            'Delete': 'حذف',
            'View': 'نمایش',
            'Actions': 'عملیات',
            'Search': 'جستجو',
            'Save': 'ذخیره',
            'Cancel': 'انصراف',
            'Are you sure you want to delete this record?': 'آیا مطمئن هستید که می‌خواهید این رکورد را حذف کنید؟',
            'Yes': 'بله',
            'No': 'خیر',
            'Create new': 'ایجاد جدید',
        }
        return mapping.get(s, s)

    # Expose common gettext aliases used by Flask-Admin templates
    app.jinja_env.globals['_'] = _translate
    app.jinja_env.globals['gettext'] = _translate
    app.jinja_env.globals['ngettext'] = lambda s, p, n: _translate(s)

    # NOTE: Sash assets are served from templates/sash/assets for legacy reasons.
    # For production, move all Sash assets to static/sash/assets and update the blueprint route if needed.

    # Initialize Flask-Admin
    admin.init_app(app, index_view=AdminIndexView(name='Home', url='/admin'))

    # Register admin views
    from .models import Post, User
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

    # Register admin view for local admin users table so `/admin/users/` works
    admin.add_view(UserAdminView(User, Session, name='کاربران', endpoint='users'))

    # Categories tree view (custom page inside Flask-Admin)
    from .admin_views import CategoriesTreeView
    admin.add_view(CategoriesTreeView(name='درخت دسته‌بندی‌ها', endpoint='categories_tree'))

    # Register blueprint
    app.register_blueprint(admin_area_bp, url_prefix='/admin')

    # Ensure requests to `/admin` (no trailing slash) redirect to the admin index `/admin/`.
    # This avoids cases where the server doesn't automatically add a trailing slash
    # and the Flask-Admin index view is not reached.
    @app.route('/admin')
    def _admin_root_redirect():
        return redirect('/admin/')

    return app

