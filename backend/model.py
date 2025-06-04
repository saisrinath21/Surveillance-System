import cv2
import threading
import police_alert
import sqlite3

model_running = False
thread = None

def detect_and_alert(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    person_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
    persons = person_cascade.detectMultiScale(gray, 1.1, 4)
    return persons

def detection_loop(user_id):
    cap = cv2.VideoCapture(0)
    while model_running:
        ret, frame = cap.read()
        if not ret:
            break
        detected = detect_and_alert(frame)
        if len(detected) > 0:
            cv2.imwrite('templates/alert_frame.jpg', frame)
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT phone_number FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            user_whatsapp_number = result
            conn.close()
            if user_whatsapp_number:
                police_alert.alert_user_via_whatsapp('templates/alert_frame.jpg', user_whatsapp_number)
                
    if not model_running:
        cap.release()

def start_detection(user_id):
    global model_running, thread
    model_running = True
    thread = threading.Thread(target=detection_loop(user_id))
    thread.start()

def stop_detection():
    global model_running
    model_running = False
