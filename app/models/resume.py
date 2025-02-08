from app.extensions import db
from datetime import datetime

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    parsed_resume = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with User
    user = db.relationship('User', backref=db.backref('resumes', lazy=True)) 