import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import DeclarativeBase
from requirements_analyzer import analyze_requirements
from plan_generator import generate_plan
from analytics import analyze_modules, analyze_complexity, analyze_timeline, get_requirements_stats
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    from models import User
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    from models import User
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Requirement
    requirements = Requirement.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', requirements=requirements)

@app.route('/analytics')
@login_required
def analytics():
    from models import Requirement
    requirements = Requirement.query.all()
    
    module_stats = analyze_modules(requirements)
    complexity_stats = analyze_complexity(requirements)
    timeline_stats = analyze_timeline(requirements)
    stats = get_requirements_stats(requirements)
    
    return render_template('analytics.html',
                         module_stats=module_stats,
                         complexity_stats=complexity_stats,
                         timeline_stats=timeline_stats,
                         stats=stats)

@app.route('/requirement/new', methods=['GET', 'POST'])
@login_required
def new_requirement():
    from models import Requirement
    
    if request.method == 'POST':
        try:
            # Log form data for debugging
            logger.info(f"New requirement submission from user {current_user.id}")
            logger.debug(f"Form data: {request.form}")
            
            # Validate required fields
            required_fields = ['project_scope', 'customization_type', 'modules_involved', 'functional_requirements']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'{field.replace("_", " ").title()} is required')
                    return render_template('requirement_form.html'), 400
            
            # Additional validation
            if len(request.form['project_scope'].strip()) < 10:
                flash('Project scope must be at least 10 characters long')
                return render_template('requirement_form.html'), 400
                
            if len(request.form['functional_requirements'].strip()) < 20:
                flash('Functional requirements must be at least 20 characters long')
                return render_template('requirement_form.html'), 400
            
            # Create requirement
            requirement = Requirement(
                user_id=current_user.id,
                project_scope=request.form['project_scope'].strip(),
                customization_type=request.form['customization_type'],
                modules_involved=request.form['modules_involved'].strip(),
                functional_requirements=request.form['functional_requirements'].strip(),
                technical_constraints=request.form.get('technical_constraints', '').strip(),
                preferred_timeline=request.form.get('preferred_timeline', '')
            )
            
            # Analyze and generate plan
            analysis = analyze_requirements(requirement)
            requirement.complexity = analysis['complexity']
            
            try:
                plan = generate_plan(analysis)
                requirement.implementation_plan = plan
            except Exception as e:
                logger.error(f"Error generating plan: {str(e)}")
                flash('Error generating implementation plan. Please try again.')
                return render_template('requirement_form.html'), 500
            
            # Save to database
            try:
                db.session.add(requirement)
                db.session.commit()
                logger.info(f"Requirement {requirement.id} created successfully")
                return redirect(url_for('plan_review', req_id=requirement.id))
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                db.session.rollback()
                flash('Error saving requirement. Please try again.')
                return render_template('requirement_form.html'), 500
                
        except Exception as e:
            logger.error(f"Unexpected error in new_requirement: {str(e)}")
            flash('An unexpected error occurred. Please try again.')
            return render_template('requirement_form.html'), 500
            
    return render_template('requirement_form.html')

@app.route('/plan/<int:req_id>')
@login_required
def plan_review(req_id):
    from models import Requirement
    requirement = Requirement.query.get_or_404(req_id)
    if requirement.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return render_template('plan_review.html', requirement=requirement)

@app.route('/plan/<int:req_id>/comment', methods=['POST'])
@login_required
def add_comment(req_id):
    from models import Requirement, Comment
    requirement = Requirement.query.get_or_404(req_id)
    
    if not request.form.get('content'):
        flash('Comment cannot be empty')
        return redirect(url_for('plan_review', req_id=req_id))
        
    comment = Comment(
        content=request.form['content'],
        user_id=current_user.id,
        requirement_id=req_id
    )
    
    db.session.add(comment)
    db.session.commit()
    flash('Comment added successfully')
    return redirect(url_for('plan_review', req_id=req_id))

@app.route('/plan/<int:req_id>/progress', methods=['POST'])
@login_required
def update_progress(req_id):
    from models import Requirement
    requirement = Requirement.query.get_or_404(req_id)
    if requirement.user_id != current_user.id:
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
    return redirect(url_for('plan_review', req_id=req_id))

with app.app_context():
    import models
    db.create_all()
