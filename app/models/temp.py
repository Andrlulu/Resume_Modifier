from typing import Dict, Any, List
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy 
from flask import Flask
from datetime import datetime



class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    city = db.Column(db.String(100))
    bio = db.Column(db.String(200))
    country = db.Column(db.String(100))


    resumes = db.relationship('Resume', back_populates='user', lazy='dynamic')
    job_descriptions = db.relationship('JobDescription', back_populates='user', lazy='dynamic')

    updated_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    
    

    def set_password(self, password):
        self.password = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password, password)
    

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    user_id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    serial_number = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    extracted_text = db.Column(db.String(5000), nullable=True)
    template = db.Column(db.Integer, nullable=False)
    parsed_resume = db.Column(db.JSON, nullable=False)
    user = db.relationship('User', back_populates='resumes')
    
    updated_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)


class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    user_id = db.Column(db.ForeignKey('users.id'), primary_key=True)
    serial_number = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(500), nullable=False)
    user = db.relationship('User', back_populates='job_descriptions')

    created_at = db.Column(db.DateTime, nullable=False)


class UserSite(db.Model):
    __tablename__ = 'user_sites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    resume_serial = db.Column(db.Integer, nullable=False)
    subdomain = db.Column(db.String(100), nullable=False, unique=True)
    html_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'resume_serial', name='uix_user_resume'),
    )
    
    def __repr__(self):
        return f'<UserSite {self.subdomain}>' 

