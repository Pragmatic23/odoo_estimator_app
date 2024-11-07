import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import DeclarativeBase
from requirements_analyzer import analyze_requirements
from plan_generator import generate_plan
from analytics import analyze_modules, analyze_complexity, get_requirements_stats
from datetime import datetime
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, validators

class Base(DeclarativeBase):
    pass

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

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

csrf = CSRFProtect(app)

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
    stats = get_requirements_stats(requirements)
    
    return render_template('analytics.html',
                         module_stats=module_stats,
                         complexity_stats=complexity_stats,
                         stats=stats)

@app.route('/requirement/new', methods=['GET', 'POST'])
@login_required
def new_requirement():
    from models import Requirement
    form = RequirementForm()
    
    if request.method == 'POST' and form.validate_on_submit():
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
    from models import Requirement
    requirement = Requirement.query.get_or_404(req_id)
    form = FlaskForm()  # Create a form for CSRF token
    return render_template('plan_review.html', requirement=requirement, form=form)

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
    form = FlaskForm()  # Create a form for CSRF
    if form.validate_on_submit():
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
    else:
        flash('Invalid form submission')
    return redirect(url_for('plan_review', req_id=req_id))

with app.app_context():
    import models
    db.create_all()
