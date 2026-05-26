from flask import current_app, jsonify, request
from extensions.extensions import db
from flask import Blueprint
from utils.jwt_utils import token_required
from models.user_model import User
from services.twilio_services import sendOTP_via_sms
import random
from datetime import datetime, timedelta
import jwt
from extensions.redis_client import redis_client

profile_bp = Blueprint(
    'profile_bp',
    __name__
)


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

# Forgot Password endpoint
# @app.route('/forgot-password', methods=['POST'])
# def forgot_password():
#     data = request.json
#     username = data.get('username')
#     phone = data.get('phone')
#     new_password = data.get('new_password')

#     # here i need to implement a functionality where i would needed to send a otp and 
#     # verify the otp and then only allow the user to reset the password

#     if not username or not phone or not new_password:
#         return jsonify({'error': 'Missing required fields'}), 400
#     con = sqlite3.connect('database.db')
#     cur = con.cursor()
#     cur.execute('SELECT * FROM users WHERE username=? AND phone=?', (username, phone))
#     user = cur.fetchone()
#     if not user:
#         con.close()
#         return jsonify({'error': 'User not found or phone number does not match'}), 404
#     cur.execute('UPDATE users SET password=? WHERE username=? AND phone=?', (new_password, username, phone))
#     con.commit()
#     con.close()
#     return jsonify({'message': 'Password reset successful'}), 200



@profile_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    data = request.get_json()
    # Implementation for updating profile
    user_id = request.user_id
    user_name = data.get('username')
    address = data.get('address')
    camera_url = data.get('camera_url')
    district = data.get('district')
    password = data.get('password')
    phone = data.get('phone')
    if user_name != request.username:
        # If username changed, generate a new token with updated username
        token = jwt.encode({
            'user_id': user_id,
            'username': user_name,
            'user_type': 'user',
            'exp': request.exp
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'message': 'Profile updated successfully', 'token': token}), 200

    try:
        user = db.session.get(User, user_id)
        user.username = user_name
        user.address = address
        # user.camera_url = camera_url
        user.district = district
        user.phone = phone
        user.password = password
        db.session.commit()
        db.session.close()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500