from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from frontend.map import build_map, noId_build_map
from backend.search_api import search
from backend.database import save, show_countries, show_cities, delete, login
from backend.borders import countries_borders
import os
from dotenv import load_dotenv

load_dotenv()

website = Flask(__name__)
website.secret_key = os.getenv("SECRET_KEY")

@website.route("/home/")
def home():
    folium_map = noId_build_map()
    folium_map.get_root().render()
    header = folium_map.get_root().header.render()
    body_html = folium_map.get_root().html.render()
    script = folium_map.get_root().script.render()

    return render_template("home.html", 
                    header=header, body_html=body_html,script=script)


@website.route("/login/", methods=["POST"])
def login_page():
    username = request.form["username"]
    password = request.form["password"]
    action = request.form["action"]

    user_id = login(username, password, action)

    if user_id == None:
        return "ERROR"

    session["user_id"] = user_id

    return redirect(url_for("index"))


@website.route("/my_home")
def index():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("home"))
    
    folium_map, countries_layer_name, city_layer_name = build_map(user_id)
    folium_map.get_root().render()

    header = folium_map.get_root().header.render()
    body_html = folium_map.get_root().html.render()
    script = folium_map.get_root().script.render()

    countries_list = show_countries(user_id)
    cities_list = show_cities(user_id)

    return render_template("my_places.html", 
                           header=header, body_html=body_html,script=script, 
                           user_id = user_id, 
                           countries_layer_name = countries_layer_name, city_layer_name = city_layer_name,
                           countries_list = countries_list, cities_list = cities_list)



@website.route("/search/", methods=["POST"])
def search_box():
    name = request.form["place"]
    full_dict = search(name)
    if full_dict is None:
        return jsonify({"Oops!": "No city or country like that! Please try again!"})
    return jsonify(full_dict)



@website.route("/save/", methods=["POST"])
def save_web():
    user_id = session.get("user_id")
    data = request.json
    name = data.get("name")
    result = search(name)
    if result is None:
        return jsonify({"found": False})
    save(user_id, result)
    return jsonify({"found": True, "status": "saved", "type": result.get("addresstype"), "country_name": result.get("country_name")})


@website.route("/places/")
def data_apdate():
    user_id = session.get("user_id")
    update_countries = show_countries(user_id)
    update_cities = show_cities(user_id)
    return render_template("list.html", countries_list = update_countries, cities_list = update_cities)


@website.route("/map-data/")
def map_data():
    user_id = session.get("user_id")
    countries = countries_borders(user_id)
    cities = show_cities(user_id)
    return jsonify({"countries": countries.data, "cities": cities})


@website.route("/delete/", methods=["POST"])
def delete_place():
    user_id = session.get("user_id")
    result = request.json
    delete(user_id, result)
    return jsonify({"success": True})


@website.route("/my_places")
def my_places():
    return render_template("my_places.html")



if __name__ == '__main__':
    website.run(debug = True)


