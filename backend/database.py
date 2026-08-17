import sqlite3
from backend.search_api import search
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "places.db"

def table_exist():                                                  
    db = sqlite3.connect(DB_PATH)      
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS Visited_countries (
        user_id INTEGER,
        country_name TEXT,
        latitude REAL,
        longitude REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS Visited_places (
        user_id INTEGER,
        city_name TEXT,
        country_name TEXT,
        latitude REAL,
        longitude REAL)""")
    db.commit()

def save_country(user_id, result):
    db = sqlite3.connect(DB_PATH)      
    c = db.cursor()
    table_exist()
    c.execute("SELECT user_id, country_name FROM Visited_countries WHERE user_id = ? AND country_name = ?",    
        (user_id, result["country_name"]))
    existing_place = c.fetchone()
    if existing_place == None:
        c.execute(
            "INSERT INTO Visited_countries VALUES(?, ?, ?, ?)",
            (user_id, result["country_name"], result["country_lat"], result["country_lon"]))
    db.commit()
    
    db.close()

def save(user_id, result):
    db = sqlite3.connect(DB_PATH)     
    c = db.cursor()
    table_exist()
    if "addresstype" in result:
        c.execute("SELECT user_id, latitude, longitude FROM Visited_places WHERE user_id = ? AND latitude = ? AND longitude = ?",    
                (user_id, result["lat"], result["lon"]))                                      
        existing_place = c.fetchone()
        if existing_place == None:                             
            c.execute(
                "INSERT INTO Visited_places VALUES(?, ?, ?, ?, ?)",
                (user_id, result["city_name"], result["country_name"], result["lat"], result["lon"]))
            db.commit()
            db.close()
            save_country(user_id, result)                   
    else:
        save_country(user_id, result)

def delete(user_id, result):
    db = sqlite3.connect(DB_PATH)      
    c = db.cursor()
    if "addresstype" in result:
        c.execute("DELETE FROM Visited_places WHERE user_id = ? AND latitude = ? AND longitude = ?",
            (user_id, result["lat"], result["lon"]))
    else:
        c.execute("DELETE FROM Visited_countries WHERE user_id = ? AND latitude = ? AND longitude = ?",
            (user_id, result["country_lat"], result["country_lon"]))
        c.execute("DELETE FROM Visited_places WHERE user_id = ? AND country_name = ?",
            (user_id, result["country_name"]))
    db.commit()
    db.close()

def show_countries(user_id):
    countries_list = []
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("SELECT latitude, longitude, country_name FROM Visited_countries WHERE user_id = ?",
        (user_id,))
    result = c.fetchall()
    countries_list ={
    country_name: (latitude, longitude)
    for latitude, longitude, country_name in result}
    return countries_list

def show_cities(user_id):
    cities_list = []
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("SELECT latitude, longitude, city_name FROM Visited_places WHERE user_id = ?",
            (user_id,))
    result = c.fetchall()
    cities_list = {
    city_name: (latitude, longitude)
    for latitude, longitude, city_name in result}
    return cities_list

def users_data():
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL)""")
    db.commit()
    db.close()


def login(username, password, action):
    users_data()
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()
    c.execute("SELECT user_id, password FROM users WHERE username = ?",
        (username,))
    user = c.fetchone()
    if action == "login":
        if user != None:
            if check_password_hash(user[1], password):
                db.close()
                return user[0]
        db.close()
        return None

    if action == "register":
        if user != None:
            db.close()
            return None
        password_hash = generate_password_hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password_hash))
        db.commit()
        user_id = c.lastrowid
        db.close()
        return user_id



          




