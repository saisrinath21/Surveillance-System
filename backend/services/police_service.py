from geopy.distance import geodesic
from geopy.geocoders import Nominatim

from extensions.extensions import db
from models.police_model import Police

geolocator = Nominatim(user_agent="geoapi")


def search_police_station(
    district,
    user_coord
):

    stations = db.session.execute(
        db.select(Police).where(
            Police.district == district
        )
    ).scalars().all()

    if not stations:

        print("[!] No police stations found")

        return None

    user_coords = (
        user_coord.latitude,
        user_coord.longitude
    )

    station_distances = []

    for station in stations:

        try:

            station_location = geolocator.geocode(
                station.address
            )

            if station_location:
                # camera_url = station.camera_url
                
                station_coords = (
                    station_location.latitude,
                    station_location.longitude
                )

                distance = geodesic(
                    user_coords,
                    station_coords
                ).kilometers

                station_distances.append(
                    (
                        distance,
                        station.phone,
                        station.address
                    )
                )

                print(
                    f"Police Station: "
                    f"{station.address} | "
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

    nearest_distance, nearest_phone, nearest_address = \
        station_distances[0]

    print(
        f"[✓] Nearest station: "
        f"{nearest_address} "
        f"({nearest_distance:.2f}km)"
    )

    return nearest_phone