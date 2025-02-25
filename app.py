import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, PasswordField, EmailField, validators
from functools import wraps
from requirements_analyzer import analyze_requirements
from plan_generator import generate_plan
from analytics import analyze_modules, analyze_complexity, get_requirements_stats
from datetime import datetime
from models import db, User, Requirement, Comment
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize CSRF protection
csrf = CSRFProtect(app)
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable CSRF by default
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Remove time limit

# Update CORS configuration
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "X-CSRF-Token"],
        "supports_credentials": True
    }
})

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db.init_app(app)

# Form classes
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class AdminCredentialsForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[validators.DataRequired()])
    new_password = PasswordField('New Password', validators=[
        validators.DataRequired(),
        validators.Length(min=6, message="Password must be at least 6 characters long"),
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.DataRequired(),
        validators.EqualTo('new_password', message='Passwords must match')
    ])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    email = EmailField('Email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

class RequirementForm(FlaskForm):
    project_scope = TextAreaField('Project Scope', validators=[validators.DataRequired()])
    customization_type = SelectField(
        'Customization Type',
        choices=[
            ('new_module', 'New Module'),
            ('workflow_adjustment', 'Workflow Adjustment'),
            ('report_customization', 'Report Customization'),
            ('integration', 'Third-party Integration')
        ],
        validators=[validators.DataRequired()]
    )
    modules_involved = StringField('Modules Involved', validators=[validators.DataRequired()])
    functional_requirements = TextAreaField('Functional Requirements', validators=[validators.DataRequired()])
    technical_constraints = TextAreaField('Technical Constraints')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need to be logged in as an admin to view this page.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes that need CSRF protection
@csrf.exempt
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_admin and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Welcome Admin!')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials')
    
    return render_template('admin/login.html', form=form)

@app.route('/admin/reset-credentials', methods=['GET', 'POST'])
@admin_required
def admin_reset_credentials():
    form = AdminCredentialsForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect', 'error')
            return render_template('admin/reset_credentials.html', form=form)
        
        try:
            current_user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Your credentials have been updated successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating admin credentials: {str(e)}")
            flash('Error updating credentials. Please try again.', 'error')
    
    return render_template('admin/reset_credentials.html', form=form)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', users=users)

@app.route('/admin/user/<int:user_id>/delete')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account')
        return redirect(url_for('admin_dashboard'))
    
    try:
        Comment.query.filter_by(user_id=user.id).delete()
        Requirement.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user')
        app.logger.error(f"Error deleting user: {str(e)}")
    
    return redirect(url_for('admin_dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken')
            return redirect(url_for('register'))
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    requirements = Requirement.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', requirements=requirements)

@app.route('/analytics')
@login_required
def analytics():
    requirements = Requirement.query.all()
    module_stats = analyze_modules(requirements)
    complexity_stats = analyze_complexity(requirements)
    stats = get_requirements_stats(requirements)
    
    return render_template('analytics.html',
                         module_stats=module_stats,
                         complexity_stats=complexity_stats,
                         stats=stats)

@app.route('/requirement/new', methods=['GET', 'POST'])
@login_required
def new_requirement():
    form = RequirementForm()
    if form.validate_on_submit():
        try:
            requirement = Requirement(
                user_id=current_user.id,
                project_scope=form.project_scope.data.strip(),
                customization_type=form.customization_type.data,
                modules_involved=form.modules_involved.data.strip(),
                functional_requirements=form.functional_requirements.data.strip(),
                technical_constraints=form.technical_constraints.data.strip() if form.technical_constraints.data else ''
            )
            
            analysis = analyze_requirements(requirement)
            requirement.complexity = analysis['complexity']
            
            try:
                plan = generate_plan(analysis)
                requirement.implementation_plan = plan
            except Exception as e:
                app.logger.error(f"Error generating plan: {str(e)}")
                flash('Error generating implementation plan. Please try again.')
                return redirect(url_for('new_requirement'))
            
            db.session.add(requirement)
            db.session.commit()
            
            flash('Requirement submitted successfully')
            return redirect(url_for('plan_review', req_id=requirement.id))
            
        except Exception as e:
            app.logger.error(f"Error saving requirement: {str(e)}")
            db.session.rollback()
            flash('Error saving requirement. Please try again.')
            return redirect(url_for('new_requirement'))
            
    return render_template('requirement_form.html', form=form)

@app.route('/plan/<int:req_id>')
@login_required
def plan_review(req_id):
    requirement = Requirement.query.get_or_404(req_id)
    if requirement.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    form = FlaskForm()
    return render_template('plan_review.html', requirement=requirement, form=form)

@app.route('/requirement/<int:req_id>/delete')
@login_required
def delete_requirement(req_id):
    requirement = Requirement.query.get_or_404(req_id)
    if requirement.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    
    try:
        Comment.query.filter_by(requirement_id=req_id).delete()
        db.session.delete(requirement)
        db.session.commit()
        flash('Requirement deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting requirement')
        app.logger.error(f"Error deleting requirement: {str(e)}")
    
    return redirect(url_for('dashboard'))

@app.route('/plan/<int:req_id>/progress', methods=['POST'])
@login_required
def update_progress(req_id):
    form = FlaskForm()
    if form.validate_on_submit():
        requirement = Requirement.query.get_or_404(req_id)
        if requirement.user_id != current_user.id and not current_user.is_admin:
            flash('Unauthorized access')
            return redirect(url_for('dashboard'))
        
        phase_progress = {}
        for phase in ['initial_setup', 'development', 'testing', 'deployment']:
            progress = int(request.form.get(phase, 0))
            phase_progress[phase] = progress
        
        requirement.phase_progress = phase_progress
        requirement.overall_progress = sum(phase_progress.values()) // len(phase_progress)
        requirement.last_updated = datetime.utcnow()
        
        if requirement.overall_progress == 100:
            requirement.status = 'completed'
        elif requirement.overall_progress > 0:
            requirement.status = 'in_progress'
        else:
            requirement.status = 'pending'
        
        db.session.commit()
        flash('Progress updated successfully')
    else:
        flash('Invalid form submission')
    return redirect(url_for('plan_review', req_id=req_id))

with app.app_context():
    db.create_all()
    
    # Create initial admin user if none exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    elif not admin.is_admin:  # Ensure existing admin user has admin privileges
        admin.is_admin = True
        admin.password_hash = generate_password_hash('admin')
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
