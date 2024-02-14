from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = 'database.db'

def create_app():
    app = Flask(__name__, template_folder='Templates')
    app.config['SECRET_KEY'] = 'etnesiktgbnesikubgsejkgseg'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views, type, lyric, auth

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(type, url_prefix='/type')
    app.register_blueprint(lyric, url_prefix="/lyrics")

    from .models import Lyric, toAdd

    with app.app_context():
        db.create_all()

    return app