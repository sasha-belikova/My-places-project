import sqlite3
from backend.search_api import search
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "places.db"

def create_db():                                                  
    with sqlite3.connect(DB_PATH) as db:
        c = db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS Visited_countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            country_name TEXT,
            latitude REAL,
            longitude REAL,
            UNIQUE(user_id, country_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS Visited_places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            city_name TEXT,
            country_name TEXT,
            latitude REAL,
            longitude REAL,
            UNIQUE(user_id, city_name, country_name))""")
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL)""")

def save_country(user_id, result):
    with sqlite3.connect(DB_PATH) as db:
        c = db.cursor()
        c.execute ("""INSERT OR IGNORE INTO Visited_countries
            (user_id, country_name, latitude, longitude) VALUES (?, ?, ?, ?)""",
            (user_id, result["country_name"], result["country_lat"], result["country_lon"]))

def save(user_id, result):
    with sqlite3.connect(DB_PATH) as db:
        c = db.cursor()
        if "addresstype" in result:
            c.execute("""INSERT OR IGNORE INTO Visited_places
                (user_id, city_name, country_name, latitude, longitude) VALUES (?, ?, ?, ?, ?)""", 
                (user_id, result["city_name"], result["country_name"], result["lat"], result["lon"]))

    save_country(user_id, result)


def delete(user_id, result):
    with sqlite3.connect(DB_PATH) as db:
        c = db.cursor()
        if result["type"] == "city":
            c.execute("DELETE FROM Visited_places WHERE user_id = ? AND id = ?",
                (user_id, result["id"]))
        elif result["type"] == "country":
            c.execute("SELECT country_name FROM Visited_countries WHERE user_id = ? AND id = ?",
                (user_id, result["id"]))
            country = c.fetchone()
            if country:
                country_name = country[0]
                c.execute("DELETE FROM Visited_countries WHERE user_id = ? AND id = ?",
                    (user_id, result["id"]))
                c.execute("DELETE FROM Visited_places WHERE user_id = ? AND country_name = ?",
                    (user_id, country_name))
            

def show_countries(user_id):
    with sqlite3.connect(DB_PATH) as db:
        c = db.cursor()
        c.execute("SELECT id, latitude, longitude, country_name FROM Visited_countries WHERE user_id = ?",
            (user_id,))
        result = c.fetchall()
    countries_list ={
        country_name: {
                "id": country_id,
                "latitude": latitude,
                "longitude": longitude}
            for country_id, latitude, longitude, country_name in result}
    return countries_list

def show_cities(user_id):
    with sqlite3.connect(DB_PATH) as db:
        c = db.cursor()
        c.execute("SELECT id, latitude, longitude, city_name FROM Visited_places WHERE user_id = ?",
                (user_id,))
        result = c.fetchall()
    cities_list = {
        city_name: {
            "id": city_id,
            "latitude": latitude,
            "longitude": longitude}
        for city_id, latitude, longitude, city_name in result}
    return cities_list


def login(username, password, action):
    with sqlite3.connect(DB_PATH) as db:
        c = db.cursor()
        c.execute("SELECT user_id, password FROM users WHERE username = ?",
            (username,))
        user = c.fetchone()
        if action == "login":
            if user != None:
                if check_password_hash(user[1], password):
                    return user[0]
            return None
        if action == "register":
            if user != None:
                return None
            password_hash = generate_password_hash(password)
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password_hash))
            user_id = c.lastrowid
            return user_id



          




