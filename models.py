from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    requirements = db.relationship('Requirement', backref='user', lazy=True)

class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_scope = db.Column(db.Text, nullable=False)
    customization_type = db.Column(db.String(50), nullable=False)
    modules_involved = db.Column(db.String(200), nullable=False)
    functional_requirements = db.Column(db.Text, nullable=False)
    technical_constraints = db.Column(db.Text)
    implementation_plan = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    complexity = db.Column(db.String(20), default='medium')
    overall_progress = db.Column(db.Integer, default=0)
    phase_progress = db.Column(db.JSON, default={
        'initial_setup': 0,
        'development': 0,
        'testing': 0,
        'deployment': 0
    })
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comments = db.relationship('Comment', backref='requirement', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirement.id'), nullable=False)
