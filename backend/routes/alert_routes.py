from flask import request, jsonify
from models.camera_model import Camera
from models.alert_model import Alert
from models.police_model import Police
from extensions.extensions import db, socketio
from flask import Blueprint
from utils.jwt_utils import token_required
from services.twilio_services import call_police, call_user
from models.user_model import User
from datetime import datetime

alert_bp = Blueprint(
    'alert_bp',
    __name__
)

@alert_bp.route('/alert/<string:alert_id>', methods=['GET'])
@token_required
def get_alert(alert_id):
    query = db.select(Alert).where(Alert.alert_id == alert_id)
    if request.user_type == 'police':
        query = query.where(Alert.police_station_id == request.user_id)
    else:
        query = query.where(Alert.user_id == request.user_id)

    alert = db.session.execute(query).scalars().first()
    if not alert:
        return jsonify({'error': 'Alert not found or access denied'}), 404

    user = db.session.get(User, alert.user_id)
    camera = db.session.get(Camera, alert.camera_id)
    alert_data = {
        'alert_id': alert.alert_id,
        'camera_id': alert.camera_id,
        'image_url': alert.image_url,
        'timestamp': alert.timestamp,
        'status': alert.status,
        'user_response': alert.user_response,
        'police_called': alert.police_called,
        'user_name': user.username if user else None,
        'user_phone': user.phone if user else None,
        'camera_name': camera.camera_name if camera else None,
        'latitude': camera.latitude if camera else None,
        'longitude': camera.longitude if camera else None
    }
    return jsonify({'alert': alert_data}), 200

@alert_bp.route('/get-police-alerts', methods=['GET'])
@token_required
def get_police_alerts():
    if request.user_type != 'police':
        return jsonify({'error': 'Access denied'}), 403

    limit = request.args.get('limit', 50, type=int)
    try:
        query = db.select(Alert).where(Alert.police_station_id == request.user_id).order_by(Alert.timestamp.desc()).limit(limit)
        alert_rows = db.session.execute(query).scalars().all()
        alerts = []
        for x in alert_rows:
            user = db.session.get(User, x.user_id)
            camera = db.session.get(Camera, x.camera_id)
            alerts.append({
                'alert_id': x.alert_id,
                'camera_id': x.camera_id,
                'image_url': x.image_url,
                'timestamp': x.timestamp,
                'status': x.status,
                'user_response': x.user_response,
                'police_called': x.police_called,
                'user_name': user.username if user else None,
                'user_phone': user.phone if user else None,
                'camera_name': camera.camera_name if camera else None,
                'latitude': camera.latitude if camera else None,
                'longitude': camera.longitude if camera else None
            })
        return jsonify({'alerts': alerts}), 200
    except Exception as e:
        print(f'Error in get_police_alerts: {str(e)}')
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/police-stations', methods=['GET'])
def get_police_stations():
    try:
        stations = db.session.execute(db.select(Police)).scalars().all()
        station_list = [
            {
                'id': station.id,
                'code': station.code,
                'phone': station.phone,
                'district': station.district,
                'latitude': station.latitude,
                'longitude': station.longitude
            }
            for station in stations
        ]
        return jsonify({'stations': station_list}), 200
    except Exception as e:
        print(f'Error in get_police_stations: {str(e)}')
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/get-alerts', methods=['GET'])
@token_required
def get_alerts():
    """Fetch alerts for the logged-in user with pagination"""
    limit = request.args.get('limit', 20, type=int)
    try:
        query = db.select(Alert).where(Alert.user_id == request.user_id).order_by(Alert.timestamp.desc()).limit(limit)
        alert_rows = db.session.execute(query).scalars().all()

        alerts = [
            {
                'alert_id': x.alert_id,
                'camera_id': x.camera_id,
                'image_url': x.image_url,
                'timestamp': x.timestamp,
                'status': x.status,
                'user_response': x.user_response,
                'police_called': x.police_called
            }
            for x in alert_rows
        ]
        return jsonify({'alerts': alerts}), 200
    except Exception as e:
        print(f'Error in get_alerts: {str(e)}')  # Debug logging
        return jsonify({'error': str(e)}), 500
    
@alert_bp.route('/police-alert-stats', methods=['GET'])
@token_required
def get_police_alert_stats():
    if request.user_type != 'police':
        return jsonify({'error': 'Access denied'}), 403

    try:
        query = db.select(Alert).where(Alert.police_station_id == request.user_id)
        alerts = db.session.execute(query).scalars().all()
        total = len(alerts)
        pending = sum(1 for x in alerts if x.status == 'pending')
        responded = sum(1 for x in alerts if x.status in ['responded', 'dispatched'])
        resolved = sum(1 for x in alerts if x.status == 'resolved')
        return jsonify({
            'total_count': total,
            'pending_count': pending,
            'responded_count': responded,
            'resolved_count': resolved
        }), 200
    except Exception as e:
        print(f'Error in get_police_alert_stats: {str(e)}')
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/police-response-metrics', methods=['GET'])
@token_required
def get_police_response_metrics():
    if request.user_type != 'police':
        return jsonify({'error': 'Access denied'}), 403

    try:
        query = db.select(Alert).where(Alert.police_station_id == request.user_id)
        alerts = db.session.execute(query).scalars().all()
        total = len(alerts)
        responded = sum(1 for x in alerts if x.status in ['responded', 'dispatched', 'resolved'])
        response_rate = round((responded / total) * 100, 2) if total else 0
        avg_response_time = 0
        return jsonify({
            'response_rate': response_rate,
            'avg_response_time': avg_response_time
        }), 200
    except Exception as e:
        print(f'Error in get_police_response_metrics: {str(e)}')
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/police-update-alert/<string:alert_id>', methods=['POST'])
@token_required
def police_update_alert(alert_id):
    if request.user_type != 'police':
        return jsonify({'error': 'Access denied'}), 403

    data = request.json or {}
    status = (data.get('status') or '').lower()
    allowed_statuses = ['pending', 'dispatched', 'responded', 'resolved', 'escalated']
    if status not in allowed_statuses:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        alert = db.session.execute(
            db.select(Alert).where(
                Alert.alert_id == alert_id,
                Alert.police_station_id == request.user_id
            )
        ).scalar_one_or_none()

        if not alert:
            return jsonify({'error': 'Alert not found or access denied'}), 404

        alert.status = status
        db.session.commit()

        payload = {
            'alert_id': alert.alert_id,
            'camera_id': alert.camera_id,
            'image_url': alert.image_url,
            'timestamp': alert.timestamp.isoformat(),
            'status': alert.status,
            'user_response': alert.user_response,
            'police_called': alert.police_called
        }

        socketio.emit('alert_update', payload, room=f'police_id:{request.user_id}')
        socketio.emit('alert_update', payload, room=f'user_id:{alert.user_id}')

        return jsonify({'message': 'Alert status updated successfully', 'alert': payload}), 200
    except Exception as e:
        db.session.rollback()
        print(f'Error in police_update_alert: {str(e)}')
        return jsonify({'error': str(e)}), 500

@alert_bp.route('/police-call-user/<string:alert_id>', methods=['POST'])
@token_required
def police_call_user(alert_id):
    if request.user_type != 'police':
        return jsonify({'error': 'Access denied'}), 403

    try:
        alert = db.session.execute(
            db.select(Alert).where(
                Alert.alert_id == alert_id,
                Alert.police_station_id == request.user_id
            )
        ).scalar_one_or_none()

        if not alert:
            return jsonify({'error': 'Alert not found or access denied'}), 404

        user = db.session.get(User, alert.user_id)
        if not user or not user.phone:
            return jsonify({'error': 'User phone number not found'}), 400

        call_result = call_user(user.phone)
        return jsonify({'message': 'Call to user initiated', 'call': call_result}), 200
    except Exception as e:
        print(f'Error in police_call_user: {str(e)}')
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
        # 1. Fetch Alert Data
        alert = db.session.execute(
            db.select(Alert).where(
                Alert.alert_id == alert_id,
                Alert.user_id == request.user_id
            )
        ).scalar_one_or_none()

        if not alert:
            return jsonify({'error': 'Alert not found or access denied'}), 404

        camera = db.session.execute(
            db.select(Camera).where(
                Camera.camera_id == alert.camera_id,
            )
        ).scalar_one_or_none()

        if response == 'NOT OK' and not camera:
            return jsonify({'error': 'Camera data not available for police dispatch'}), 400

        # 3. Process Business Logic
        if response == 'OK':
            alert.status = 'resolved'
            alert.user_response = response
        elif response == 'NOT OK':
            alert.status = 'escalated'
            alert.user_response = response
            # Call police service safely using fetched camera attributes
            try:
                call_result = call_police(alert.alert_id, camera.latitude, camera.longitude, camera.phone)
                print(f"call_police result for alert {alert.alert_id}: {call_result}")
                if isinstance(call_result, dict) and call_result.get('station_id'):
                    alert.police_station_id = call_result['station_id']
            except Exception as warn_err:
                print(f"Warning: call_police failed: {warn_err}")
                # Continue with escalation even if police call fails

        # 4. Commit to Database
        db.session.commit()
        payload = {
            'alert_id': alert.alert_id,
            'camera_id': alert.camera_id,
            'image_url': alert.image_url,
            'timestamp': alert.timestamp.isoformat(),
            'status': alert.status,
            'user_response': alert.user_response,
            'police_called': alert.police_station_id,
            'user_name': db.session.get(User, alert.user_id).username if db.session.get(User, alert.user_id) else None,
            'user_phone': db.session.get(User, alert.user_id).phone if db.session.get(User, alert.user_id) else None,
            'latitude': camera.latitude if camera else None,
            'longitude': camera.longitude if camera else None,
        }
        print(f"Emitting alert_update to user room: user_id:{request.user_id}")
        socketio.emit('alert_update', payload, room=f"user_id:{request.user_id}")
        if alert.police_station_id:
            print(f"Emitting alert_update to police room: police_id:{alert.police_station_id}")
            socketio.emit('alert_update', payload, room=f"police_id:{alert.police_station_id}")
        
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

@alert_bp.route('/police-resolve-alert/<string:alert_id>', methods=['POST'])
@token_required
def police_resolve_alert(alert_id):
    if request.user_type != 'police':
        return jsonify({'error': 'Access denied'}), 403

    try:
        alert = db.session.execute(
            db.select(Alert).where(
                Alert.alert_id == alert_id,
                Alert.police_station_id == request.user_id
            )
        ).scalar_one_or_none()

        if not alert:
            return jsonify({'error': 'Alert not found or access denied'}), 404

        alert.status = 'resolved'
        db.session.commit()

        socketio.emit(
            'alert_update',
            {
                'alert_id': alert.alert_id,
                'camera_id': alert.camera_id,
                'image_url': alert.image_url,
                'timestamp': alert.timestamp.isoformat(),
                'status': alert.status,
                'user_response': alert.user_response,
                'police_called': alert.police_station_id
            },
            room=f"police_id:{request.user_id}"
        )
        socketio.emit(
            'alert_update',
            {
                'alert_id': alert.alert_id,
                'camera_id': alert.camera_id,
                'image_url': alert.image_url,
                'timestamp': alert.timestamp.isoformat(),
                'status': alert.status,
                'user_response': alert.user_response,
                'police_called': alert.police_station_id
            },
            room=f"user_id:{alert.user_id}"
        )

        return jsonify({'message': 'Alert resolved successfully', 'alert': {'alert_id': alert.alert_id, 'status': alert.status}}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500