from twilio.rest import Client
import os
from dotenv import load_dotenv
from utils.phone_utils import format_indian_phone_number
from flask import current_app
from datetime import datetime
from models.alert_model import Alert
from extensions.extensions import db
import uuid
from services.aws_service import upload_image_to_s3 
from flask import jsonify
from geopy.geocoders import Nominatim

from services.police_service import search_police_station


load_dotenv()

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
FROM_NUMBER = os.getenv('FROM_NUMBER')
SMS_NUMBER = os.getenv('SMS')
client = Client(ACCOUNT_SID, AUTH_TOKEN)

geolocator = Nominatim(user_agent="emergency_alert")

def alert_user_via_call(frame_or_path, user_number, user_id):
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
            with current_app.app_context():
                try:
                    alert = {
                        'alert_id': alert_id,
                        'user_id': user_id,
                        'image_url': image_url,
                        # 'camera_url': camera_url,
                        'timestamp': datetime.utcnow()
                    }
                    db.session.add(Alert(**alert))
                    db.session.commit()
                    print(f"Alert logged to database for user {user_id}")
                except Exception as e:
                    print(f"Warning: Could not log alert to database: {str(e)}")
        
        # Format phone number for Twilio call (E.164 format)
        formatted_user_number = format_indian_phone_number(user_number)
        
        if not FROM_NUMBER or not ACCOUNT_SID or not AUTH_TOKEN:
            raise Exception("Twilio credentials not configured. Set FROM_NUMBER, ACCOUNT_SID, AUTH_TOKEN in .env")
        
        call = client.calls.create(
            from_=FROM_NUMBER,
            to=formatted_user_number,
            twiml='<Response><Say>Alert. An intruder has entered the area. If you confirm whether he or she is allowed or not, we will take necessary actions.</Say></Response>'
        )
        print(f"[✓] Call alert sent. Call SID: {call.sid}")
        return {"status": "sent", "url": image_url, "sid": call.sid}
    
    except Exception as e:
        print(f"Error sending Call alert: {str(e)}")
        raise


def sendOTP_via_sms(phone_number, otp):
    try:
        formatted_number = format_indian_phone_number(phone_number)
        message = client.messages.create(
            body=f"Your OTP for confirming the alert is: {otp} and it will expire in 5 minutes. Please do not share this OTP with anyone.",
            from_=SMS_NUMBER,
            to=formatted_number
        )
        print(f"OTP sent successfully. Message SID: {message.sid}")
        return {"status": "sent", "sid": message.sid}
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        raise

def call_police(user_address, user_district, user_phone_number):
    """
    Initiate emergency: find nearest police station and create conference call
    """
    location = geolocator.geocode(user_address)
    if not location:
        print(f"Could not geocode user address: {user_address}")
        return jsonify({"error": "Could not find location for the given address."})

    print(f"User location: {location.address}")
        
    police_phone_number = search_police_station(user_district, location)

    if not police_phone_number:
        print(f"No reachable police stations found")
        return jsonify({"error": "Could not find a nearby police station in the database."})

    try:
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
        return jsonify({"message": "Conference call initiated between user and nearest police station."})
    except Exception as e: 
        print(f"Error initiating conference call: {str(e)}")
        return jsonify({"error": f"Error initiating conference call: {str(e)}"})
