from geopy.geocoders import Nominatim
from twilio.rest import Client
import requests
import sqlite3
from geopy.distance import geodesic
from flask import jsonify, Flask, request
import boto3
from botocore.exceptions import NoCredentialsError
import os
import cv2
import io
from datetime import datetime
import frontend.user_app

app = Flask(__name__)
geolocator = Nominatim(user_agent="geoapi")

from dotenv import load_dotenv
load_dotenv()


ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
FROM_NUMBER = os.getenv('FROM_NUMBER')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET')
AWS_S3_REGION = os.getenv('AWS_S3_REGION')

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def upload_image_to_s3(frame_or_path):
    """
    Upload image to S3 from either:
    - OpenCV frame (numpy array)
    - Local file path (string)
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION
    )
    try:
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alert_frame_{timestamp}.jpg"
        
        if isinstance(frame_or_path, str):
            # If it's a file path, read and upload
            with open(frame_or_path, 'rb') as f:
                s3.upload_fileobj(f, AWS_S3_BUCKET, filename, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
        else:
            # If it's an OpenCV frame (numpy array), encode to JPEG in memory
            _, buffer = cv2.imencode('.jpg', frame_or_path)
            image_bytes = io.BytesIO(buffer)
            s3.upload_fileobj(image_bytes, AWS_S3_BUCKET, filename, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
        
        url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{filename}"
        return url
    except NoCredentialsError:
        raise Exception("AWS credentials not available.")
    except Exception as e:
        raise Exception(f"Failed to upload to S3: {str(e)}")

def alert_user_via_whatsapp(frame_or_path, user_whatsapp_number, user_id=None):
    """
    Send WhatsApp alert with image to user.
    Also logs the alert to database for history tracking.
    """
    try:
        image_url = upload_image_to_s3(frame_or_path)
        
        # Log alert to database if user_id is provided
        if user_id:
            try:
                con = sqlite3.connect('database.db')
                cur = con.cursor()
                cur.execute('''INSERT INTO alerts (user_id, image_url, status) 
                             VALUES (?, ?, 'pending')''', (user_id, image_url))
                con.commit()
                con.close()
                print(f"Alert logged to database for user {user_id}")
            except Exception as e:
                print(f"Warning: Could not log alert to database: {str(e)}")
        
        message = client.messages.create(
            body=(
                "🚨 *Movement Detected at Your Gate!*\n"
                "Please review the image and reply with:\n"
                "`OK` – All good\n"
                "`NOT OK` – Call the police immediately"
            ),
            from_='whatsapp:+14155238886',  # Twilio sandbox number
            to=f'whatsapp:{user_whatsapp_number}',
            media_url=[image_url]
        )
        print(f"[✓] WhatsApp alert sent. Message SID: {message.sid}")
        return {"status": "sent", "url": image_url, "sid": message.sid}
        frontend.user_app.incoming_whatsapp()
    
    except Exception as e:
        print(f"[✗] Error sending WhatsApp alert: {str(e)}")
        raise

def search_police_station(district, user_coord):
    # Connect to the database and get all police stations in the district
    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    cur.execute("SELECT address, phone FROM police WHERE district = ?", (district,))
    stations = cur.fetchall()
    con.close()

    if not stations:
        print("[!] No police stations found in database")
        return None
    
    user_coords = (user_coord.latitude, user_coord.longitude)
    station_distances = []
    
    for address, phone in stations:
        try:
            station_location = geolocator.geocode(address)
            if station_location:
                station_coords = (station_location.latitude, station_location.longitude)
                distance = geodesic(user_coords, station_coords).kilometers
                station_distances.append((distance, phone, address))
                print(f"Police Station: {address} | Distance: {distance:.2f}km")
        except Exception as e:
            print(f"Error geocoding police address '{address}': {str(e)}")
            continue

    if not station_distances:
        print("[!] Could not geocode any police stations")
        return None

    station_distances.sort(key=lambda x: x[0])
    nearest_distance, nearest_phone, nearest_address = station_distances[0]
    
    print(f"[✓] Nearest police station selected: {nearest_address} ({nearest_distance:.2f}km away)")
    return nearest_phone

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

        print(f"Initiating call to police: {police_phone_number}")
        client.calls.create(
            to=police_phone_number,
            from_=FROM_NUMBER,
            twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )

        print(f"Initiating call to user: {user_phone_number}")
        client.calls.create(
            to=user_phone_number,
            from_=FROM_NUMBER,
            twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )

        print(f"Conference call initiated")
        return jsonify({"message": "Conference call initiated between user and nearest police station."})
    except Exception as e: 
        print(f"[✗] Error initiating conference call: {str(e)}")
        return jsonify({"error": f"Error initiating conference call: {str(e)}"})
