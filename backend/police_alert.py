import webbrowser
from geopy.geocoders import Nominatim
from twilio.rest import Client
import requests
import sqlite3
from geopy.distance import geodesic

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
    print(f"WhatsApp alert sent. Message SID: {message.sid}")

def search_police_station(district, user_address):
    # Connect to the database and get all police stations in the district
    con = sqlite3.connect('police_database.db')
    cur = con.cursor()
    cur.execute("SELECT address, phone FROM police WHERE district = ?", (district,))
    stations = cur.fetchall()
    con.close()

    if not stations:
        return None

    # Get user's coordinates
    geolocator = Nominatim(user_agent="geoapi")
    user_location = geolocator.geocode(user_address)
    if not user_location:
        return None
    user_coords = (user_location.latitude, user_location.longitude)

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
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(user_address)
    if not location:
        print("Could not find location for the given address.")
        return

    print(f"User location: {location.address}")
    district = location.raw.get("address", {}).get("country", "") or \
               location.raw.get("address", {}).get("state", "") or \
               location.raw.get("address", {}).get("district", "")

    police_phone_number = search_police_station(district)

    if not police_phone_number:
        print("Could not find a nearby police station in the database.")
        return

    print(f"Nearest police station phone: {police_phone_number}")

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

        print("Conference call initiated between user and nearest police station.")
    except Exception as e:
        print("Error initiating conference call:", e)
