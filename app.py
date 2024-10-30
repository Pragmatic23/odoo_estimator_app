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
    requirements = Requirement.query.all()  # Get all requirements for analysis
    
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
        requirement = Requirement(
            user_id=current_user.id,
            project_scope=request.form['project_scope'],
            customization_type=request.form['customization_type'],
            modules_involved=request.form['modules_involved'],
            functional_requirements=request.form['functional_requirements'],
            technical_constraints=request.form['technical_constraints'],
            preferred_timeline=request.form['preferred_timeline']
        )
        
        analysis = analyze_requirements(requirement)
        requirement.complexity = analysis['complexity']
        plan = generate_plan(analysis)
        requirement.implementation_plan = plan
        
        db.session.add(requirement)
        db.session.commit()
        
        return redirect(url_for('plan_review', req_id=requirement.id))
    return render_template('requirement_form.html')

@app.route('/plan/<int:req_id>')
@login_required
def plan_review(req_id):
    from models import Requirement
    requirement = Requirement.query.get_or_404(req_id)
    return render_template('plan_review.html', requirement=requirement)

@app.route('/requirement/<int:req_id>/delete')
@login_required
def delete_requirement(req_id):
    from models import Requirement
    requirement = Requirement.query.get_or_404(req_id)
    if requirement.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    
    db.session.delete(requirement)
    db.session.commit()
    flash('Requirement deleted successfully')
    return redirect(url_for('dashboard'))

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
