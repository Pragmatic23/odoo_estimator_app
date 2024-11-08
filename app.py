import os
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from flask_wtf.csrf import CSRFError
from wtforms import StringField, TextAreaField, SelectField, PasswordField, EmailField, validators
from functools import wraps
from requirements_analyzer import analyze_requirements
from plan_generator import generate_plan
from analytics import analyze_modules, analyze_complexity, get_requirements_stats
from datetime import datetime
from models import db, User, Requirement, Comment

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# CSRF Configuration
csrf = CSRFProtect(app)
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_SSL_STRICT'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db.init_app(app)

# Form classes
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
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

# Error Handlers
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return make_response(render_template('error.html', message='CSRF token is missing or invalid'), 400)

# Headers for iframe access
@app.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = 'ALLOW-FROM *'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

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

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/admin')
def admin_welcome():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/welcome.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_admin and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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
        try:
            db.session.commit()
            login_user(user)
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.')
            app.logger.error(f"Error creating user: {str(e)}")
            return redirect(url_for('register'))
            
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = FlaskForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    requirements = Requirement.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', requirements=requirements)

if __name__ == '__main__':
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
            
    app.run(host='0.0.0.0', port=5000, debug=True)
