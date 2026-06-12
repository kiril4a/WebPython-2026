from flask import Flask

from .config import DevelopmentConfig
from .extensions import db, login_manager, mail, migrate
from .models import User


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Увійдіть у систему для доступу до цієї сторінки."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .admin.routes import admin_bp
    from .mail.routes import mail_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(mail_bp, url_prefix="/mail")

    with app.app_context():
        db.create_all()
        from .seed import create_demo_data

        create_demo_data()

    return app
