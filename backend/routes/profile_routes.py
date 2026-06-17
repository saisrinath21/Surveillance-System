from flask import current_app, jsonify, request
from geopy.geocoders import Nominatim
from models.camera_model import Camera
from extensions.extensions import db, socketio
from flask import Blueprint
from utils.jwt_utils import token_required
from models.user_model import User
from services.twilio_services import sendOTP_via_sms
import random
import uuid
from datetime import datetime, timedelta
import jwt
from extensions.redis_client import redis_client


profile_bp = Blueprint(
    'profile_bp',
    __name__
)

geolocator = Nominatim(user_agent="surveillance_app")

def geolocate_district(latitude, longitude):
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location.raw.get("address", {}).get("district", "Unknown")

@profile_bp.route('/generate-otp/<string:user_id>', methods=['GET'])
@token_required
def generate_otp(user_id):
    # Generate a random 6-digit OTP
    otp = str(random.randint(0, 999999))
    otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    six_digits_otp = otp.zfill(6)  # Ensure OTP is 6 digits with leading zeros if necessary

    user = db.session.execute(db.select(User).filter(User.id == user_id)).scalars().first()
    user_phone_number = user.phone if user else None

    redis_client.setex(
        f"otp:{user_id}",
        300,
        six_digits_otp
    )

    if not user_phone_number:
        return jsonify({'error': 'User phone number not found'}), 404

    sendOTP_via_sms(user_phone_number, six_digits_otp)
    return jsonify({'message': 'OTP generated and sent successfully'}), 200

@profile_bp.route('/verify-otp/<string:user_id>', methods=['POST'])
@token_required
def verify_otp(user_id):
    data = request.get_json()
    otp = data.get('otp')
    if not otp:
        return jsonify({'error': 'OTP not found'}), 404

    stored_otp = redis_client.get(f"otp:{user_id}")
    if not stored_otp:
        return jsonify({'error': 'OTP has expired'}), 400

    if otp == stored_otp:
        redis_client.delete(f"otp:{user_id}")
        redis_client.delete(f"otp_expiry:{user_id}")
        return jsonify({'valid': True}), 200
    else:
        return jsonify({'valid': False}), 400

@profile_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    data = request.get_json() or {}
    user_id = request.user_id
    user_name = data.get('username')
    password = data.get('password')
    phone = data.get('phone')

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    username_changed = user_name is not None and user_name != request.username

    if user_name is not None:
        user.username = user_name
    if password is not None:
        user.password = password
    if phone is not None:
        user.phone = phone

    try:
        db.session.commit()
        db.session.close()

        if username_changed:
            token = jwt.encode({
                'user_id': user_id,
                'username': user_name,
                'user_type': 'user',
                'exp': datetime.utcnow() + timedelta(hours=2)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'message': 'Profile updated successfully', 'token': token}), 200

        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500
    
@profile_bp.route('/add-camera', methods=['POST'])
@token_required
def add_camera():
    data = request.get_json() or {}
    camera_name = data.get('camera_name')
    camera_url = data.get('camera_rtsp') or data.get('camera_url')
    phone = data.get('phone')
    latitude = data.get('latitude') or data.get('camera_latitude')
    longitude = data.get('longitude') or data.get('camera_longitude')
    if not all([camera_name, camera_url, phone, latitude, longitude]):
        return jsonify({'error': 'Missing required camera fields'}), 400
    try:
        camera_id = str(uuid.uuid4())[:30]
        district = geolocate_district(latitude, longitude)
        new_camera = Camera(
            camera_id=camera_id,
            user_id=request.user_id,
            camera_name=camera_name,
            camera_url=camera_url,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            district=district,
        )
        socketio.emit(
            'camera_update',
            {
                'camera_id': camera_id,
                'camera_name': camera_name,
                'camera_url': camera_url,
                'phone': phone,
                'latitude': latitude,
                'longitude': longitude,
                'model_active': False
            },
            room=f"user_id: {request.user_id}"
        )
        db.session.add(new_camera)
        db.session.commit()
        return jsonify({'message': 'Camera added successfully', 'camera_id': camera_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add camera: {str(e)}'}), 500

@profile_bp.route('/get-cameras', methods=['GET'])
@token_required
def get_cameras():
    try:
        if request.user_id is None:
            return jsonify({'error': 'User ID not found in token'}), 400
        cameras = db.session.execute(
            db.select(Camera).where(Camera.user_id == request.user_id)
        ).scalars().all()
        result = [
            {
                'camera_id': c.camera_id,
                'camera_name': c.camera_name,
                'camera_url': c.camera_url,
                'phone': c.phone,
                'latitude': c.latitude,
                'longitude': c.longitude,
                'model_active': c.model_active
            }
            for c in cameras
        ]
        return jsonify({'cameras': result}), 200
    except Exception as e:
        current_app.logger.exception('Failed to fetch cameras')
        return jsonify({'error': f'Failed to fetch cameras: {str(e)}'}), 500

@profile_bp.route('/edit-camera-details', methods=['POST'])
@token_required
def edit_camera_details():
    data = request.get_json()
    camera_id = data.get('camera_id')
    camera_name = data.get('camera_name')
    camera_url = data.get('camera_url')
    phone = data.get('phone')
    camera_latitude = data.get('camera_latitude')
    camera_longitude = data.get('camera_longitude')
    if not all([camera_id, camera_name, camera_url, phone, camera_latitude, camera_longitude]):
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        camera = db.session.get(Camera, camera_id)
        camera.camera_name = camera_name
        camera.camera_url = camera_url
        camera.phone = phone
        camera.latitude = camera_latitude
        camera.longitude = camera_longitude
        camera.district = geolocate_district(camera_latitude, camera_longitude)
        socketio.emit(
            'camera_update',
            {
                'camera_id': camera_id,
                'camera_name': camera_name,
                'camera_url': camera_url,
                'phone': phone,
                'latitude': camera_latitude,
                'longitude': camera_longitude,
                'model_active': camera.model_active
            },
            room=f"user_id: {request.user_id}"
        )
        db.session.commit()
        db.session.close()
        return jsonify({'message': 'Camera details updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to edit camera details: {str(e)}'}), 500
    
@profile_bp.route('/delete-camera/<string:camera_id>', methods=['DELETE'])
@token_required
def delete_camera(camera_id):
    try:
        camera = db.session.get(Camera, camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        db.session.delete(camera)
        db.session.commit()
        db.session.close()
        return jsonify({'message': 'Camera deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete camera: {str(e)}'}), 500
    
@profile_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    try:
        
        user = db.session.get(User, request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'username': user.username,
            'phone': user.phone
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch profile: {str(e)}'}), 500
    
