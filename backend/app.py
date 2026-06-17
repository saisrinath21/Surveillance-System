from flask import Flask
from flask_cors import CORS
from flask_socketio import join_room

from config.config import Config
from extensions.extensions import db, socketio
from dotenv import load_dotenv
import os
import jwt

load_dotenv()

FRONTEND_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000,http://localhost:3001,http://localhost:3002')
# Parse comma-separated origins for Socket.IO and strip any surrounding quotes
FRONTEND_ORIGINS = [url.strip().strip('"').strip("'") for url in FRONTEND_URL.split(',') if url.strip()]

def create_app():

    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": FRONTEND_ORIGINS}})

    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins=FRONTEND_ORIGINS)
    print(f"Socket.IO allowed origins: {FRONTEND_ORIGINS}")

    # IMPORT BLUEPRINTS INSIDE FUNCTION
    from routes.auth_routes import auth_bp
    from routes.alert_routes import alert_bp
    from routes.profile_routes import profile_bp
    from routes.detection_routes import detection_bp

    @socketio.on('connect')
    def handle_connect(auth):
        token = auth.get('token') if auth else None
        if not token:
            print('Socket connect rejected: no token')
            return False
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            if payload.get('user_type') == 'police':
                police_room = f"police_id:{payload['user_id']}"
                join_room(police_room)
                print(f"Socket connected for police {payload['user_id']} in room {police_room}")
            else:
                user_room = f"user_id:{payload['user_id']}"
                join_room(user_room)
                print(f"Socket connected for user {payload['user_id']} in room {user_room}")
            return True
        except Exception as e:
            print(f"Socket auth failed: {e}")
            return False


    app.register_blueprint(auth_bp)

    app.register_blueprint(alert_bp)

    app.register_blueprint(profile_bp)

    app.register_blueprint(detection_bp)

    return app