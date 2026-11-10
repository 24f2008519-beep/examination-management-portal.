from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "your_secret_key"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emp.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    from app.models import user

    with app.app_context():
        db.create_all()

    from app.routes.main import main
    app.register_blueprint(main)
    print(app.url_map)
    return app