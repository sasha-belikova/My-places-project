from backend.database import show_countries, show_cities
import folium
import json
from pathlib import Path

def all_countries():
    geojson_path = Path(__file__).resolve().parent.parent / "data" / "countries.geojson"

    with open(geojson_path, "r", encoding="utf-8") as file:
        full_geojson = json.load(file)
    return folium.GeoJson(full_geojson)



def countries_borders(user_id):
    full_geojson = all_countries()
    chosen_countries = show_countries(user_id)
    for feature in full_geojson.data["features"][:]:    
        country_name = feature["properties"]["NAME"]    
        if not(country_name in chosen_countries):
            full_geojson.data["features"].remove(feature)
    return full_geojson


def one_country(country_name):
    full_geojson = all_countries()
    for feature in full_geojson.data["features"][:]:    
        name = feature["properties"]["NAME"]  
        if name != country_name:
            full_geojson.data["features"].remove(feature)
    return full_geojson

