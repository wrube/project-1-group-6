from geopy.geocoders import Nominatim
import pandas as pd
import geopy
from datetime import datetime
from geopy.distance import geodesic
from shapely.ops import nearest_points
from pathlib import Path


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



def convert_milliseconds_to_year_month_day(timestamp_ms):
    """This function will convert the millisecond datetime utc given in the USGS API into a year, month, day tuple

    Args:
        timestamp_ms (integer): datetime provided in the USGS API in milliseconds   

    Returns:
        tuple(integer, integer, integer): A tuple in the form (year, month, day)
    """
    # Convert milliseconds to seconds
    timestamp_seconds = timestamp_ms / 1000.0

    # Convert timestamp to datetime object
    utc_datetime = datetime.utcfromtimestamp(timestamp_seconds)

    # Extract year, month, and day
    year = utc_datetime.year
    month = utc_datetime.month
    day = utc_datetime.day

    return year, month, day


def consolidate_csv_files(directory, min_filename_length):
    # List all CSV files in the directory
    csv_files = [file for file in Path(directory).rglob('*.csv') if len(file.name) >= min_filename_length]

    # Read each CSV file into a DataFrame
    dataframes = []
    for file in csv_files:
        df = pd.read_csv(file)
        dataframes.append(df)

    # Merge DataFrames into a single DataFrame
    merged_df = pd.concat(dataframes, ignore_index=True)

    return merged_df

################### below this line is experimental ######################




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
    

def find_nearest_country_and_distance(latitude, longitude):
    # Perform reverse geocoding to get the country's name
    geolocator = Nominatim(user_agent="nearest_country_finder", timeout=10)
    location = geolocator.reverse((latitude, longitude), language='en')
    country_name = location.raw['address'].get('country', 'Country not found')

    # Use GeoPandas to retrieve the country's geometry
    gdf = gpd.tools.geocode(country_name, provider='nominatim', user_agent="nearest_country_finder")
    
    if gdf.empty:
        print("Unable to retrieve country geometry.")
        return None, None

    # Extract the country's geometry
    country_geometry = gdf['geometry'].iloc[0]

    # Convert the given latitude and longitude to a Shapely Point
    target_point = Point(longitude, latitude)

    # Find the nearest point on the country's geometry to the target point
    nearest_point_country, _ = nearest_points(country_geometry, target_point)

    # Calculate distance using Haversine formula
    distance = nearest_point_country.distance(target_point)

    return country_name, distance

if __name__ == "__main__":
    # Example coordinates (somewhere in the Atlantic Ocean)
    latitude_ocean = 0.0
    longitude_ocean = -30.0

    # Find nearest country and distance
    country, distance = find_nearest_country_and_distance(latitude_ocean, longitude_ocean)

    if country is not None and distance is not None:
        print(f"The coordinates {latitude_ocean}, {longitude_ocean} are nearest to {country}.")
        print(f"Distance to nearest land: {distance:.2f} kilometers.")
    else:
        print("Unable to determine the nearest country and distance.")