from geopy.geocoders import Nominatim
from datetime import datetime


def get_country(lat, lon):
    """This function will return the country of the input latitude and longitude. This function utilises the geopy module

    This function is inspired from https://www.geeksforgeeks.org/get-the-city-state-and-country-names-from-latitude-and-longitude-using-python/

    Args:
        lat (float): latitude from -90 to 90
        lon (float): longitude from -180 to 180 

    Returns:
        string: name of country
    """
    # Initialize the Nominatim geocoder
    geolocator = Nominatim(user_agent="my_geocoder")

    # Construct the location string
    location = geolocator.reverse((lat, lon), language='en')

    # Extract the country name from the location information
    try:
        country_name = location.raw['address'].get('country', 'Country not found')
    except AttributeError as e:
        country_name = "Country not found"

    return country_name


def convert_utc_to_year_month_day(utc_timestamp):
    # Convert UTC timestamp to datetime object
    utc_datetime = datetime.utcfromtimestamp(utc_timestamp)

    # Extract year, month, and day
    year = utc_datetime.year
    month = utc_datetime.month
    day = utc_datetime.day

    return year, month, day


def convert_milliseconds_to_year_month_day(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_seconds = timestamp_ms / 1000.0

    # Convert timestamp to datetime object
    utc_datetime = datetime.utcfromtimestamp(timestamp_seconds)

    # Extract year, month, and day
    year = utc_datetime.year
    month = utc_datetime.month
    day = utc_datetime.day

    return year, month, day


def find_location_info(latitude, longitude):
    geolocator = Nominatim(user_agent="location_info_finder")

    try:
        # Perform reverse geocoding
        location = geolocator.reverse((latitude, longitude), language='en')

        # Extract the location type
        geo_type = location.raw.get("type")

        if geo_type == 'land':

            # Extract country, water body, and land/water information
            country = location.raw['address'].get('country', 'Country not found')
        else:

            water_body = location.raw['address'].get('ocean', 'Body of water not found')
            country = "unknown"
        

        return country, water_body, geo_type

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None