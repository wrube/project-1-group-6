from geopy.geocoders import Nominatim
import numpy as np
import pandas as pd
import geopy
from datetime import datetime
import geopandas as gpd
from geopy.distance import geodesic
from shapely.ops import nearest_points
from pathlib import Path
from shapely.geometry import Point
from pprint import pprint

crs_code = "EPSG:4326"

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
        # print(f"number of columns in df is {len(df.columns)}")
        dataframes.append(df)

    # Merge DataFrames into a single DataFrame
    merged_df = pd.concat(dataframes, ignore_index=False, join='inner')

    return merged_df

def count_earthquakes_in_country_in_year(countries, earthquakes, year, countries_buffered=False):
    earthquakes_in_year = earthquakes.loc[earthquakes["year"] == year]
    joined_gdf = gpd.sjoin(earthquakes_in_year, countries, how='inner', predicate='within')

    if countries_buffered:
        buffered = " within 2deg border"
    else:
        buffered = ""
    
    # Count the number of points within each polygon
    earthquake_counts = pd.DataFrame(joined_gdf.groupby('NAME').size()).rename(columns = {0: f"Earthquake count{buffered} {year}"})
    return earthquake_counts

def create_buffer_with_degrees(gdf, buffer_radius_deg):
    buffered_gdf = gdf.copy()
    buffered_gdf['geometry'] = buffered_gdf['geometry'].buffer(buffer_radius_deg)
    return buffered_gdf

def convert_df_to_gdf(dataframe, lon_column, lat_column, crs_code):
    geometry = [Point(xy) for xy in zip(dataframe[lon_column], dataframe[lat_column])]
    gdf = gpd.GeoDataFrame(dataframe, geometry=geometry, crs=crs_code)
    return gdf

def create_world_bin_dataframe():
    # create rectangular bins
    bin_size = 10 # degree increments
    start_lat = -90
    end_lat = 90
    start_long = -180
    end_long = 180

    min_lats = np.arange(start_lat, end_lat, bin_size)
    max_lats = np.arange(start_lat + bin_size, end_lat, bin_size)
    min_longs = np.arange(start_long, end_long, bin_size)
    max_longs = np.arange(start_long + bin_size, end_long, bin_size)

    # create rectangular limits array with subarrays with elements [minimum_latitude, maximum_latitude, minimum_longitude, maximum_longitude]
    bins = {}
    for i in range(len(min_lats)):
        for j in range(len(min_longs)):
            bins[f"{i}_{j}"] = {
                "bin_lat": min_lats[i] + bin_size/2,
                "bin_lon": min_longs[j] + bin_size/2
                }
    earthquake_spatial_distribution = pd.DataFrame(bins).T
    earthquake_spatial_distribution.rename_axis("bin_id", inplace=True)
    return earthquake_spatial_distribution

################### below this line is experimental ######################

if __name__ == "__main__":
    df = create_world_bin_dataframe()
    print(df)