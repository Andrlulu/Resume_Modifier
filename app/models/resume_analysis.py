from app.extensions import db

class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'))
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'))
    analysis_result = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp()) 