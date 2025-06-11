from geopy.geocoders import Nominatim
from twilio.rest import Client
import requests
import sqlite3
from geopy.distance import geodesic
from flask import jsonify, Flask, request
app = Flask(__name__)

geolocator = Nominatim(user_agent="geoapi")

# Twilio and Imgur credentials
ACCOUNT_SID = 'your_account_sid'
AUTH_TOKEN = 'your_auth_token'
FROM_NUMBER = 'your_twilio_number'
IMGUR_CLIENT_ID = 'your_imgur_client_id'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def upload_image_to_imgur(image_path):
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    with open(image_path, "rb") as img:
        response = requests.post("https://api.imgur.com/3/image", headers=headers, files={"image": img})
    response.raise_for_status()
    return response.json()["data"]["link"]

def alert_user_via_whatsapp(image_path, user_whatsapp_number):
    image_url = upload_image_to_imgur(image_path)
    message = client.messages.create(
        body=(
            "\ud83d\udea8 *Movement Detected at Your Gate!*\n"
            "Please review the image and reply with:\n"
            "`OK` – All good\n"
            "`NOT OK` – Call the police immediately"
        ),
        from_='whatsapp:+14155238886',  # Twilio sandbox number
        to=f'whatsapp:{user_whatsapp_number}',
        media_url=[image_url]
    )
    return jsonify({"message": "WhatsApp alert sent", "sid": message.sid})

def search_police_station(district, user_coord):
    # Connect to the database and get all police stations in the district
    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    cur.execute("SELECT address, phone FROM police WHERE district = ?", (district,))
    stations = cur.fetchall()
    con.close()

    if not stations:
        return None
    # Calculate coordinates for the user
    user_coords = (user_coord.latitude, user_coord.longitude)
    # Calculate distances
    station_distances = []
    for address, phone in stations:
        station_location = geolocator.geocode(address)
        if station_location:
            station_coords = (station_location.latitude, station_location.longitude)
            distance = geodesic(user_coords, station_coords).kilometers
            station_distances.append((distance, phone))

    if not station_distances:
        return None

    nearest_phone = None
    min_distance = float('inf')

    for distance, phone in station_distances:
        if distance < min_distance:
            min_distance = distance
            nearest_phone = phone
            
    return nearest_phone

def call_police(user_address, user_phone_number):
    location = geolocator.geocode(user_address)
    if not location:
        return jsonify({"Could not find location for the given address."})

    print(f"User location: {location.address}")
    district = location.raw.get("address", {}).get("district", "")
    if not district:
        return jsonify({"error": "District information could not be extracted from the address."})

    police_phone_number = search_police_station(district, location)

    if not police_phone_number:
        return jsonify({"Could not find a nearby police station in the database."})

    try:
        conference_name = "EmergencyAlertConference"

        client.calls.create(
            to=police_phone_number,
            from_=FROM_NUMBER,
            twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )

        client.calls.create(
            to=user_phone_number,
            from_=FROM_NUMBER,
            twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )

        return jsonify({"Conference call initiated between user and nearest police station."})
    except Exception as e: 
        return jsonify({"error": f"Error initiating conference call: {str(e)}"})
