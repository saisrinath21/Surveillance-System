from flask import current_app, request, jsonify
from flask.cli import load_dotenv
from models.user_model import User
from models.police_model import Police
from extensions.extensions import db
from flask import Blueprint
from utils.jwt_utils import token_required
import jwt
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from utils.district_utils import geolocate_district, geolocator
from dotenv import load_dotenv
import os
load_dotenv()


auth_bp = Blueprint(
    'auth_bp',
    __name__
)

ADMIN = os.getenv('ADMIN')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['username', 'password', 'phone']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({'error': f'Missing fields: {", ".join(missing_fields)}'}), 400

    try:
        user_id = str(uuid.uuid4())[:30]
        new_user = User(
            id = user_id,
            username = data['username'],
            password = data['password'],
            phone = data['phone']
        )
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User already exists'}), 409

    return jsonify({'message': 'Registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = db.session.execute(db.select(User).where(User.username == data['username'], User.password == data['password'])).scalars().first()
    db.session.commit()
    if user:
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'user_type': 'user',
            'exp': datetime.utcnow() + timedelta(hours=2)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'id': user.id,
            'username': user.username
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/police-register', methods=['POST'])
def police_register():
    data = request.get_json() or {}
    required_fields = ['token', 'code', 'password', 'phone', 'latitude', 'longitude']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({'error': f"Missing fields: {', '.join(missing_fields)}"}), 400

    if not ADMIN:
        return jsonify({'error': 'Admin token is not configured on the server'}), 500

    if data.get('token') != ADMIN:
        return jsonify({'error': 'Invalid admin token'}), 401

    try:
        police_id = str(uuid.uuid4())[:30]
        latitude = data['latitude']
        longitude = data['longitude']

        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        district = geolocate_district(latitude, longitude)

        new_police = Police(
            id=police_id,
            code=data['code'],
            password=data['password'],
            latitude=latitude,
            longitude=longitude,
            district=district,
            phone=data['phone'],
        )
        db.session.add(new_police)
        db.session.commit()
        return jsonify({'message': 'Police Registered'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Police code/phone already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/police-login', methods=['POST'])
def police_login():
    data = request.json
    if not data.get('code') or not data.get('password'):
        return jsonify({'error': 'Missing code or password'}), 400
    
    user = db.session.execute(db.select(Police).where(Police.code == data['code'], Police.password == data['password'])).scalars().first()
    db.session.commit()
    if user:
        # Generate JWT token for police
        token = jwt.encode({
            'user_id': user.id,
            'police_code': user.code,
            'user_type': 'police',
            'exp': datetime.utcnow() + timedelta(hours=2),
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Police Login successful',
            'token': token,
            'id': user.id,
            'police_code': user.code
        }), 200
    else:
        return jsonify({'error': 'Invalid police credentials'}), 401


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    # With JWT, logout is handled on the client side by deleting the token
    # This endpoint can be used for cleanup/logging purposes if needed
    return jsonify({'message': 'Logged out successfully'}), 200