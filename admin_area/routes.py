"""
Admin Area Routes
Authentication routes for admin panel
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from pathlib import Path

from .forms import LoginForm
from .models import get_user_by_username

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

