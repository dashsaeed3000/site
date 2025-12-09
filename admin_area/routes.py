"""
Admin Area Routes
Authentication routes for admin panel
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from pathlib import Path

from .forms import LoginForm
from .models import get_user_by_username
from app.repositories.db import get_scoped_session
from sqlalchemy import func, and_
from app.models.models import Products, Categories, Blogs, ProductComments

# Set template folder for this blueprint
template_folder = str(Path(__file__).parent / 'templates')
admin_area_bp = Blueprint('admin_area', __name__, template_folder=template_folder)


@admin_area_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if current_user.is_authenticated:
        if hasattr(current_user, 'is_admin') and current_user.is_admin():
            # Redirect to Flask-Admin panel
            return redirect('/admin')
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is disabled.', 'error')
                return render_template('login.html', form=form)
            
            if not user.is_admin():
                flash('Access denied. Admin privileges required.', 'error')
                return render_template('login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page:
                next_page = '/admin'
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)


@admin_area_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_area.login'))

@admin_area_bp.route('/api/stats/categories', methods=['GET'])
@login_required
def api_category_stats():
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        return jsonify({'error': 'forbidden'}), 403

    Session = get_scoped_session()
    db = Session()
    try:
        results = db.query(
            Categories.Title,
            func.count(Products.Id).label('count')
        ).join(
            Products, Categories.Id == Products.CategoryId, isouter=True
        ).filter(
            Categories.IsDeleted == False
        ).group_by(Categories.Id, Categories.Title).all()

        labels = [row[0] or 'بدون دسته‌بندی' for row in results]
        counts = [int(row[1] or 0) for row in results]
        return jsonify({'labels': labels, 'counts': counts})
    except Exception as e:
        # Return JSON error instead of raising to avoid breaking the page
        import logging
        logging.getLogger(__name__).exception('api_category_stats failed')
        return jsonify({'error': 'internal_server_error', 'message': str(e)}), 500
    finally:
        db.close()


@admin_area_bp.route('/api/stats/summary', methods=['GET'])
@login_required
def api_summary_stats():
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin():
        return jsonify({'error': 'forbidden'}), 403

    Session = get_scoped_session()
    db = Session()
    try:
        active_products = db.query(Products).filter(
            and_(Products.IsDeleted == False, Products.IsActive == True)
        ).count()
        published_blogs = db.query(Blogs).filter(
            and_(Blogs.IsDeleted == False, Blogs.IsPublished == True)
        ).count()
        total_comments = db.query(ProductComments).filter(
            ProductComments.IsDeleted == False
        ).count()
        featured_products = db.query(Products).filter(
            and_(Products.IsDeleted == False, Products.IsActive == True, Products.IsFeatured == True)
        ).count()

        labels = ['محصولات فعال', 'مقالات منتشر شده', 'نظرات', 'محصولات ویژه']
        values = [active_products, published_blogs, total_comments, featured_products]
        return jsonify({'labels': labels, 'values': values})
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception('api_summary_stats failed')
        return jsonify({'error': 'internal_server_error', 'message': str(e)}), 500
    finally:
        db.close()
