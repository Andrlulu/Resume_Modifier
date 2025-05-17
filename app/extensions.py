from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager() 

@login_manager.user_loader
def load_user(user_id):
    from app.models.temp import User
    return User.query.get(int(user_id))