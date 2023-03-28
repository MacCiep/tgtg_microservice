from flask import Flask

from .extensions import db
from .routes import main
import os

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL_TGTG")

    db.init_app(app)

    app.register_blueprint(main)

    return app