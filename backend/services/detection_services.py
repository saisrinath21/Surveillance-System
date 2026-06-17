import cv2
import threading
from models.camera_model import Camera
from models.user_model import User 
from services.twilio_services import alert_user_via_call
from ultralytics import YOLO
from dotenv import load_dotenv
from extensions.extensions import db, socketio
from flask import current_app
from extensions.redis_client import redis_client

thread = None

# Initialize the YOLO model (use standard pretrained weights)
model = YOLO('yolov8n.pt')

def detect_and_alert(frame):
    results = model.predict(frame, classes=[0])
    return results

def detection_loop(camera_id, app):
    redis_key = f"detection:{camera_id}"

    with app.app_context():
        camera = db.session.execute(db.select(Camera).where(Camera.camera_id == camera_id)).scalars().first()
        if not camera:
            return

        cap = cv2.VideoCapture(camera.camera_url)

        try:
            while True:
                status = redis_client.get(redis_key)
                
                # Check if status exists and is "running"
                if status != "running":
                    print(f"Stopping loop. Status: {status}")
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                detected = detect_and_alert(frame)
                
                if len(detected[0].boxes) > 0:
                    print("Intruder detected!")
                    if camera.phone:
                        # Set to stopped immediately
                        redis_client.setex(redis_key, 3600, "stopped")
                        
                        # Update DB
                        camera.model_active = False
                        db.session.commit()
                        socketio.emit(
                            'camera_update',
                            {
                                'camera_id': camera_id,
                                'model_active': False
                            },
                            room=f"user_id: {camera.user_id}"
                        )
                        
                        alert_user_via_call(
                            frame,
                            camera.phone,
                            camera_id,
                            camera.user_id,
                        )
        finally:
            cap.release()

def start_detection(camera_id):
    global thread
    redis_client.setex(
        f"detection:{camera_id}",
        3600,
        "running"
    )
    app = current_app._get_current_object()
    thread = threading.Thread(target=detection_loop, args=(camera_id, app))  # Initialize with a dummy thread
    thread.start()

def stop_detection(camera_id):
    global thread
    redis_client.setex(
        f"detection:{camera_id}",
        3600,
        "stopped"
    )
    camera = db.session.execute(db.select(Camera).where(Camera.camera_id == camera_id)).scalars().first()
    if camera:
        camera.model_active = False
        db.session.commit()