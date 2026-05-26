import cv2
import threading
from models.user_model import User 
from services.twilio_services import alert_user_via_call
from ultralytics import YOLO
from dotenv import load_dotenv
from extensions.extensions import db
from flask import current_app

load_dotenv()
model_running = False
thread = None

# Initialize the YOLO model (use standard pretrained weights)
model = YOLO('yolov8n.pt')

def detect_and_alert(frame):
    results = model.predict(frame, classes=[0])
    return results

def detection_loop(user_id, app):
    global model_running

    with app.app_context():
        user = db.session.execute(db.select(User).where(User.id == user_id)).scalars().first()
        # if(user.camera_url is None):
        #     cap = cv2.VideoCapture(0)  # Use default webcam if no camera URL is provided
        # else:
        cap = cv2.VideoCapture(0)  # Assuming user has a camera_url field in the database

        try:
            while model_running:
                ret, frame = cap.read()
                if not ret:
                    break
                detected = detect_and_alert(frame)
                if len(detected[0].boxes) > 0:
                    print("Fetching user WhatsApp number from database...")
                    user_whatsapp_number = user.phone if user else None
                    if user_whatsapp_number:
                        model_running = False
                        alert_user_via_call(
                            frame,
                            user_whatsapp_number,
                            user_id,
                            # user.camera_url
                        )
        finally:
            cap.release()
def start_detection(user_id):
    global model_running, thread
    model_running = True
    app = current_app._get_current_object()  # Ensure we have the app context
    thread = threading.Thread(target=detection_loop, args=(user_id, app))  # Initialize with a dummy thread
    thread.start()

def stop_detection():
    global model_running
    model_running = False
