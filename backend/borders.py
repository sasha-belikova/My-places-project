from backend.database import show_countries, show_cities
import folium
import json
from pathlib import Path

geojson_path = Path(__file__).resolve().parent.parent / "data" / "countries.geojson"

with open(geojson_path, "r", encoding="utf-8") as file:
    full_geojson = json.load(file)

def all_countries():
    return folium.GeoJson(full_geojson)


def countries_borders(user_id):
    chosen_countries = show_countries(user_id)
    countries = {
        "type": "FeatureCollection",
        "features": []
    }
    for feature in full_geojson["features"]:
        country_name = feature["properties"]["NAME"]
        if country_name in chosen_countries:
            countries["features"].append(feature)
    return folium.GeoJson(countries)

def one_country(country_name):
    full_geojson = all_countries()
    for feature in full_geojson.data["features"][:]:    
        name = feature["properties"]["NAME"]  
        if name != country_name:
            full_geojson.data["features"].remove(feature)
    return full_geojson