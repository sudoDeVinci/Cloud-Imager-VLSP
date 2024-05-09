from flask import Flask
from flask_login import LoginManager
from Devinci.db.services.user import UserService
from Devinci.db.Entities import UserEntity

def create_app():
    app = Flask(__name__)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(ID: str) -> UserEntity:
        return UserService.get_user(userID = ID)

    from Devinci.views import views
    from Devinci.auth import auth
    from Devinci.api import api
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api/")
    
    @app.context_processor
    def inject_enumerate():
        return dict(enumerate=enumerate)

    return app