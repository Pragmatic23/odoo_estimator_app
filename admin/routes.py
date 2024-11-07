from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from app import db
from models import User, Requirement
from flask_wtf import FlaskForm
from wtforms import PasswordField, validators

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need to be an admin to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

class PasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min=6, message="Password must be at least 6 characters long")
    ])

@admin.route('/')
@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    try:
        users = User.query.all()
        requirements = Requirement.query.all()
        form = FlaskForm()
        password_form = PasswordResetForm()
        
        stats = {
            'total_users': len(users),
            'total_requirements': len(requirements),
            'admin_users': len([u for u in users if u.is_admin])
        }
        
        return render_template('admin/dashboard.html', 
                             users=users, 
                             stats=stats, 
                             form=form, 
                             password_form=password_form)
    except Exception as e:
        current_app.logger.error(f"Admin dashboard error: {str(e)}")
        flash('Error accessing admin dashboard', 'error')
        return redirect(url_for('dashboard'))

@admin.route('/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password():
    form = PasswordResetForm()
    if form.validate_on_submit():
        try:
            user_id = request.form.get('user_id')
            if not user_id:
                flash('User ID is required', 'error')
                return redirect(url_for('admin.dashboard'))
                
            user = User.query.get_or_404(user_id)
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash(f'Password reset successful for user {user.username}', 'success')
        except Exception as e:
            current_app.logger.error(f"Password reset error: {str(e)}")
            db.session.rollback()
            flash('Error resetting password', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'error')
                
    return redirect(url_for('admin.dashboard'))

@admin.route('/make-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    form = FlaskForm()
    if form.validate_on_submit():
        try:
            user = User.query.get_or_404(user_id)
            user.is_admin = True
            db.session.commit()
            flash(f'User {user.username} is now an admin', 'success')
        except Exception as e:
            current_app.logger.error(f"Make admin error: {str(e)}")
            db.session.rollback()
            flash('Error updating admin status', 'error')
    return redirect(url_for('admin.dashboard'))

@admin.route('/remove-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_admin(user_id):
    form = FlaskForm()
    if form.validate_on_submit():
        try:
            if user_id == current_user.id:
                flash('You cannot remove your own admin privileges', 'error')
                return redirect(url_for('admin.dashboard'))
                
            user = User.query.get_or_404(user_id)
            user.is_admin = False
            db.session.commit()
            flash(f'Admin privileges removed from user {user.username}', 'success')
        except Exception as e:
            current_app.logger.error(f"Remove admin error: {str(e)}")
            db.session.rollback()
            flash('Error updating admin status', 'error')
    return redirect(url_for('admin.dashboard'))
