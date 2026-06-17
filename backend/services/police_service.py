from sqlalchemy import func
from extensions.extensions import db
from models.police_model import Police
from utils.district_utils import geolocate_district, geodesic


def search_police_station(user_coords):
    try:
        user_lat = float(user_coords['latitude'])
        user_lon = float(user_coords['longitude'])
    except (TypeError, ValueError) as e:
        print(f"Invalid user coordinates: {user_coords} | {e}")
        return None

    district = geolocate_district(user_lat, user_lon)
    normalized_district = district.strip().lower() if isinstance(district, str) else district
    print(f"search_police_station: user=({user_lat},{user_lon}), district='{district}'")

    stations = []
    if isinstance(normalized_district, str) and normalized_district and normalized_district != 'unknown':
        stations = db.session.execute(
            db.select(Police).where(
                func.lower(Police.district) == normalized_district
            )
        ).scalars().all()

    if not stations:
        print(f"[!] No police stations found in district '{district}' or district lookup unavailable; using all stations")
        stations = db.session.execute(db.select(Police)).scalars().all()
        if not stations:
            print("[!] No police stations found in the database")
            return None

    station_distances = []
    user_coord = (user_lat, user_lon)
    for station in stations:
        try:
            station_coords = (
                float(station.latitude),
                float(station.longitude)
            )

            # `geodesic` helper returns a kilometer value (float), not a Distance
            # object in `utils/district_utils.py`. Use the returned value directly
            # but guard in case the helper is changed to return a Distance object.
            raw_distance = geodesic(user_coord, station_coords)
            distance = float(raw_distance.kilometers) if hasattr(raw_distance, 'kilometers') else float(raw_distance)

            station_address = f"{station.latitude},{station.longitude}"
            station_distances.append((distance, station.id, station.phone, station_address))

            print(
                f"Police Station: "
                f"{station_address} | "
                f"Distance: {distance:.2f}km"
            )

        except Exception as e:

            print(
                f"Error geocoding "
                f"{station.address}: {str(e)}"
            )

            continue

    if not station_distances:

        print("[!] No reachable police stations")

        return None

    station_distances.sort(
        key=lambda x: x[0]
    )

    nearest_distance, nearest_id, nearest_phone, nearest_address = \
        station_distances[0]
        
    print(
        f"[✓] Nearest station: "
        f"{nearest_address} "
        f"({nearest_distance:.2f}km)"
    )

    return {
        'station_id': nearest_id,
        'phone': nearest_phone,
        'distance_km': nearest_distance
    }