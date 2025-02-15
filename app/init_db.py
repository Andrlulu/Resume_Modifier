from app.server import app
from app.extensions import db
from app.models.user import User
from app.models.resume import Resume
from app.models.job_description import JobDescription

def init_db():
    with app.app_context():
        print("Creating database tables...")
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 