from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'  # Matches your existing table name
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    # Define relationship without backref
    resumes = db.relationship('Resume', back_populates='user_ref')
    job_descriptions = db.relationship('JobDescription', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)