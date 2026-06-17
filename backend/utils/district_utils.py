from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="surveillance_app")

def geolocate_district(latitude, longitude):
    try:
        location = geolocator.reverse(f"{latitude}, {longitude}")
        if not location or not hasattr(location, 'raw'):
            return 'Unknown'

        address = location.raw.get('address', {})
        for field in [
            'district',
            'city_district',
            'state_district',
            'county',
            'city',
            'town',
            'village',
            'suburb',
            'municipality'
        ]:
            value = address.get(field)
            if value:
                return value

        return 'Unknown'
    except Exception as e:
        print(f"District geolocation failed for {latitude},{longitude}: {e}")
        return 'Unknown'

def geodesic(coord1, coord2):
    from geopy.distance import geodesic as geopy_geodesic
    """Return a geopy Distance object for the given coordinate pair.

    Callers may use the returned object's `kilometers` attribute to get
    the numeric distance in kilometers.
    """
    return geopy_geodesic(coord1, coord2)