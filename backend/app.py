from flask import Flask
from flask_cors import CORS

from config.config import Config
from extensions.extensions import db

def create_app():

    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config.from_object(Config)

    db.init_app(app)

    # IMPORT BLUEPRINTS INSIDE FUNCTION
    from routes.auth_routes import auth_bp
    from routes.alert_routes import alert_bp
    from routes.profile_routes import profile_bp
    from routes.detection_routes import detection_bp

    app.register_blueprint(auth_bp)

    app.register_blueprint(alert_bp)

    app.register_blueprint(profile_bp)

    app.register_blueprint(detection_bp)

    return app