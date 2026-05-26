from flask import current_app, request, jsonify
from flask import Blueprint
from utils.jwt_utils import token_required
from services.detection_services import start_detection, stop_detection, model_running

detection_bp = Blueprint(
    'detection_bp',
    __name__
)
@detection_bp.route('/toggle-detection', methods=['POST'])
@token_required
def toggle_detection():
    data = request.get_json()
    status = data.get('status')

    try:
        if status:
            start_detection(request.user_id)  # Pass the app context to start_detection
        else:
            stop_detection()
        return jsonify({'message': f'Model Toggled for {request.username}'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to toggle model: {str(e)}'}), 500

@detection_bp.route('/detection-status', methods=['GET'])
@token_required
def get_detection_status():
    try:
        return jsonify({'model_running': model_running}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get detection status: {str(e)}'}), 500
    

