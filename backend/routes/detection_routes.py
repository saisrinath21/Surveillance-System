from flask import current_app, request, jsonify
from flask import Blueprint
from utils.jwt_utils import token_required
from services.detection_services import start_detection, stop_detection
from extensions.extensions import db, socketio
from models.camera_model import Camera
detection_bp = Blueprint(
    'detection_bp',
    __name__
)
@detection_bp.route('/toggle-detection', methods=['POST'])
@token_required
def toggle_detection():
    data = request.get_json() or {}
    status = data.get('status')
    camera_id = data.get('camera_id') or request.args.get('camera_id')
    if camera_id is None:
        return jsonify({'error': 'camera_id is required'}), 400
    try:
        # Start or stop detection service for this camera
        camera = db.session.get(Camera, camera_id)
        if status:
            start_detection(camera_id)
        else:
            stop_detection(camera_id)

        return jsonify({'message': f'Model Toggled for camera {camera_id}', 'model_active': status}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to toggle model: {str(e)}'}), 500