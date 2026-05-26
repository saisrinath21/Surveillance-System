from flask import request, jsonify
from models.alert_model import Alert
from extensions.extensions import db
from flask import Blueprint
from utils.jwt_utils import token_required
from services.twilio_services import call_police
from models.user_model import User

alert_bp = Blueprint(
    'alert_bp',
    __name__
)

@alert_bp.route('/alert/<string:alert_id>', methods=['GET'])
@token_required
def get_alert(alert_id):
    alert = db.session.execute(db.select(Alert).where(Alert.alert_id == alert_id)).scalars().first()
    db.session.commit()
    alert_data = {
        'alert_id': alert.alert_id,
        'user_id': alert.user_id,
        'image_url': alert.image_url,
        'timestamp': alert.timestamp,
        'status': alert.status,
        'user_response': alert.user_response,
        'police_called': alert.police_called
    } if alert else None
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    return jsonify({'alert': alert_data}), 200

@alert_bp.route('/get-alerts', methods=['GET'])
@token_required
def get_alerts():
    """Fetch all alerts for the logged-in user"""
    limit = request.args.get('limit', 20, type=int)
    
    try:
        alert = db.session.execute(
            db.select(Alert)
            .where(Alert.user_id == request.user_id)
            .order_by(Alert.timestamp.desc())
            .limit(limit)
        ).scalars().all()
            
        alerts = [
            {
                'alert_id': x.alert_id,
                'user_id': x.user_id,
                'image_url': x.image_url,
                'timestamp': x.timestamp,
                'status': x.status,
                'user_response': x.user_response,
                'police_called': x.police_called
            }
            for x in alert
        ]
        return jsonify({'alerts': alerts}), 200
    except Exception as e:
        print(f'Error in get_alerts: {str(e)}')  # Debug logging
        import traceback
        traceback.print_exc()  # Full traceback
        return jsonify({'error': str(e)}), 500
    
@alert_bp.route('/update-alert-response/<string:alert_id>', methods=['POST']) # Added type routing
@token_required
def update_alert_response(alert_id):
    """Update alert response from web interface"""
    data = request.json or {} # Prevents NoneType error if body is empty
    response = data.get('response', '').upper()
    
    if response not in ['OK', 'NOT OK']:
        return jsonify({'error': 'Invalid response. Must be OK or NOT OK'}), 400
    
    try:
        # 1. Fetch User Data
        user_data = db.session.execute(
            db.select(User).where(User.id == request.user_id)
        ).scalar_one_or_none()
        
        if not user_data:
            return jsonify({'error': 'User not found'}), 404
        
        # 2. Fetch Alert Data
        alert = db.session.execute(
            db.select(Alert).where(Alert.alert_id == alert_id, Alert.user_id == request.user_id)
        ).scalar_one_or_none()
        
        if not alert:
            return jsonify({'error': 'Alert not found or access denied'}), 404
            
        # 3. Process Business Logic
        if response == 'OK':
            alert.status = 'resolved'
            alert.user_response = response
        elif response == 'NOT OK':
            alert.status = 'escalated'
            alert.user_response = response
            # Call police service safely using fetched user attributes
            call_police(user_data.address, user_data.district, user_data.phone)
        
        # 4. Commit to Database
        db.session.commit()
        
        # 5. Return JSON format explicitly
        return jsonify({
            'message': 'Alert response recorded successfully',
            'alert': {
                'alert_id': alert.alert_id,
                'status': alert.status,
                'user_response': alert.user_response
            }
        }), 200
        
    except Exception as e:
        db.session.rollback() # Rollback changes if database error happens
        # Log the exception 'e' here for debugging
        return jsonify({'error': 'An internal database error occurred'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500