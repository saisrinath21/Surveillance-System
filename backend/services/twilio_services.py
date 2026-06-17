import token
import jwt
from twilio.rest import Client
import os
from dotenv import load_dotenv
from utils.phone_utils import format_indian_phone_number
from flask import jsonify
from datetime import datetime
from models.alert_model import Alert
from models.user_model import User
from models.camera_model import Camera
from extensions.extensions import db, socketio
import uuid
from services.aws_service import upload_image_to_s3 
from geopy.geocoders import Nominatim
from services.police_service import search_police_station
from twilio.twiml.voice_response import VoiceResponse


load_dotenv()

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
FROM_NUMBER = os.getenv('FROM_NUMBER')
client = Client(ACCOUNT_SID, AUTH_TOKEN)

geolocator = Nominatim(user_agent="emergency_alert")

def alert_user_via_call(frame_or_path, user_number, camera_id, user_id):
    """
    Send WhatsApp alert with image to user.
    Also logs the alert to database for history tracking.
    """
    try: 
        # Generate unique alert ID
        alert_id = str(uuid.uuid4())[:12]  # Shorter UUID: f47ac10b-58cc
        
        image_url = upload_image_to_s3(frame_or_path)
        # Log alert to database if user_id is provided
        if user_id:
            try:
                alert_data = {
                    'user_id': user_id,
                    'alert_id': alert_id,
                    'image_url': image_url,
                    'camera_id': camera_id,
                    'timestamp': datetime.utcnow()
                }
                new_alert = Alert(**alert_data)
                db.session.add(new_alert)
                db.session.commit()
                socketio.emit(
                    'alert_update',
                    {
                        'alert_id': new_alert.alert_id,
                        'camera_id': new_alert.camera_id,
                        'image_url': new_alert.image_url,
                        'timestamp': new_alert.timestamp.isoformat(),
                        'status': new_alert.status,
                        'user_response': new_alert.user_response,
                        'police_called': new_alert.police_called
                    },
                    room=f"user_id:{user_id}"
                )
                print(f"Alert logged to database for user {user_id}")
            except Exception as e:
                print(f"Warning: Could not log alert to database: {str(e)}")
        
        # Format phone number for Twilio call (E.164 format)
        formatted_user_number = format_indian_phone_number(user_number)
        
        if not FROM_NUMBER or not ACCOUNT_SID or not AUTH_TOKEN:
            raise Exception("Twilio credentials not configured. Set FROM_NUMBER, ACCOUNT_SID, AUTH_TOKEN in .env")
        
        twiml_response = VoiceResponse()
        twiml_response.say("Alert. An intruder has entered the area. Please confirm if this person is allowed.")
        call = client.calls.create(
            from_=FROM_NUMBER,
            to=formatted_user_number,
            twiml=twiml_response
        )
        print(f"[✓] Call alert sent. Call SID: {call.sid}")
        print(f"TwiML: {twiml_response}")
        return {"status": "sent", "url": image_url, "sid": call.sid}
    
    except Exception as e:
        print(f"Error sending Call alert: {str(e)}")
        raise

def sendOTP_via_sms(phone_number, otp):
    try:
        formatted_number = format_indian_phone_number(phone_number)
        message = client.messages.create(
            body=f"Your OTP is: {otp} and it will expire in 30 sec. Please do not share this OTP with anyone.",
            from_=FROM_NUMBER,
            to=formatted_number
        )
        print(f"OTP sent successfully. Message SID: {message.sid}")
        return {"status": "sent", "sid": message.sid}
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        raise

def call_police(alert_id, user_latitude, user_longitude, user_phone_number):
    """
    Initiate emergency: find nearest police station and create conference call
    """
    user_cords = {
        'latitude': user_latitude,
        'longitude': user_longitude
    }
    police_station = search_police_station(user_cords)
    
    if not police_station:
        print(f"No reachable police stations found")
        raise Exception("Could not find a nearby police station in the database.")

    police_phone_number = police_station['phone']

    try:
        alert = db.session.execute(
            db.select(Alert).where(Alert.alert_id == alert_id)
        ).scalars().first()
        if not alert:
            raise Exception(f"Alert not found: {alert_id}")

        alert.police_station_id = police_station['station_id']
        db.session.flush()
        user = db.session.get(User, alert.user_id)
        camera = db.session.get(Camera, alert.camera_id)
        police_room = f"police_id:{police_station['station_id']}"
        print(f"Emitting alert_update to police room {police_room} for alert {alert.alert_id}")
        socketio.emit(
            'alert_update',
            {
                'alert_id': alert.alert_id,
                'camera_id': alert.camera_id,
                'image_url': alert.image_url,
                'timestamp': alert.timestamp.isoformat(),
                'status': alert.status,
                'user_response': alert.user_response,
                'police_called': alert.police_station_id,
                'user_name': user.username if user else None,
                'user_phone': user.phone if user else None,
                'latitude': camera.latitude if camera else None,
                'longitude': camera.longitude if camera else None,
            },
            room=police_room
        )
        conference_name = "EmergencyAlertConference"
        
        if not FROM_NUMBER or not ACCOUNT_SID or not AUTH_TOKEN:
            raise Exception("Twilio credentials not configured. Set FROM_NUMBER, ACCOUNT_SID, AUTH_TOKEN in .env")
        
        # Ensure phone numbers are in E.164 format
        police_phone_formatted = format_indian_phone_number(police_phone_number) if police_phone_number.isdigit() or '+' not in police_phone_number else police_phone_number
        user_phone_formatted = format_indian_phone_number(user_phone_number) if user_phone_number.isdigit() or '+' not in user_phone_number else user_phone_number
        
        print(f"Initiating call to police: {police_phone_formatted}")
        police_call = client.calls.create(
            to=police_phone_formatted,
            from_=FROM_NUMBER,
            twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )
        print(f"Police call initiated. SID: {police_call.sid}")

        print(f"Initiating call to user: {user_phone_formatted}")
        user_call = client.calls.create(
            to=user_phone_formatted,
            from_=FROM_NUMBER,
            twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )
        print(f"User call initiated. SID: {user_call.sid}")

        print(f"Conference call initiated")
        return {
            'station_id': police_station['station_id'],
            'police_phone': police_phone_formatted,
            'user_phone': user_phone_formatted,
            'police_call_sid': police_call.sid,
            'user_call_sid': user_call.sid
        }
    except Exception as e: 
        print(f"Error initiating conference call: {str(e)}")
        raise


def call_user(user_phone_number):
    """Call the user directly from police action."""
    try:
        if not FROM_NUMBER or not ACCOUNT_SID or not AUTH_TOKEN:
            raise Exception("Twilio credentials not configured. Set FROM_NUMBER, ACCOUNT_SID, AUTH_TOKEN in .env")

        if isinstance(user_phone_number, str) and user_phone_number.startswith('+'):
            user_phone_formatted = user_phone_number
        else:
            user_phone_formatted = format_indian_phone_number(user_phone_number)

        user_call = client.calls.create(
            from_=FROM_NUMBER,
            to=user_phone_formatted,
            twiml='<Response><Say>Please stay on the line. A police unit is responding to your alert.</Say></Response>'
        )
        print(f"User call initiated. SID: {user_call.sid}")
        return {'user_call_sid': user_call.sid, 'user_phone': user_phone_formatted}
    except Exception as e:
        print(f"Error initiating call to user: {str(e)}")
        raise
