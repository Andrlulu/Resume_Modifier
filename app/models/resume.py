from app.extensions import db

class Resume(db.Model):
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(100), nullable=False)
    extracted_text = db.Column(db.Text)
    parsed_resume = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    # Define the back_populates relationship
    user_ref = db.relationship('User', back_populates='resumes') 