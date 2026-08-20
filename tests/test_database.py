import pytest
import backend.database as database

#Creating database fot tests
@pytest.fixture
def test_db(tmp_path):
    database.DB_PATH = tmp_path / "test_places.db"
    database.create_db()
    yield



#Tests for saving and showing cities and countries
def test_save_country(test_db):
    fake_id = 1
    fake_result = {
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save_country(fake_id, fake_result)
    countries = database.show_countries(fake_id)
    assert countries == {
        "Austria": {
            "id": 1,
            "latitude": 1.84719,
            "longitude": 2.4583129670}}


def test_save_city(test_db):
    fake_id = 5
    fake_result = {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "7.84719",
        "lon": "3.4583129670",
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save(fake_id, fake_result)
    countries = database.show_countries(fake_id)
    cities = database.show_cities(fake_id)
    assert countries == {
        "Austria": {
            "id": 1,
            "latitude": 1.84719,
            "longitude": 2.4583129670}}
    assert cities == {
        "Vienna": {
            "id": 1,
            "latitude": 7.84719,
            "longitude": 3.4583129670}}


def test_save_country_duplicate(test_db):
    fake_id = 32
    fake_result = {
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save_country(fake_id, fake_result)
    database.save_country(fake_id, fake_result)
    countries = database.show_countries(fake_id)
    assert len(countries) == 1

def test_save_city_duplicate(test_db):
    fake_id = 1
    fake_result = {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "7.84719",
        "lon": "3.4583129670",
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save(fake_id, fake_result)
    database.save(fake_id, fake_result)
    cities = database.show_cities(fake_id)
    countries = database.show_countries(fake_id)
    assert len(countries) == 1
    assert len(cities) == 1

def test_save_country_with_save(test_db):
    fake_id = 22
    fake_result = {
            "country_name": "Austria",
            "country_lat": "1.84719",
            "country_lon": "2.4583129670"}
    database.save(fake_id, fake_result)
    countries = database.show_countries(fake_id)
    cities = database.show_cities(fake_id)
    assert cities == {}
    assert countries == {
        "Austria": {
            "id": 1,
            "latitude": 1.84719,
            "longitude": 2.4583129670}}

def test_show_countries_empty(test_db):
    fake_id = 100
    countries = database.show_countries(fake_id)
    assert countries == {}


def test_show_cities_empty(test_db):
    fake_id = 100
    cities = database.show_cities(fake_id)
    assert cities == {}

def test_same_country_different_users(test_db):
    fake_result = {
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save_country(1, fake_result)
    database.save_country(2, fake_result)
    countries_user1 = database.show_countries(1)
    countries_user2 = database.show_countries(2)
    assert "Austria" in countries_user1
    assert "Austria" in countries_user2

    


    
# Tests for delete
def test_delete_city(test_db):
    fake_id = 1
    fake_result = {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "7.84719",
        "lon": "3.4583129670",
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save(fake_id, fake_result)
    cities = database.show_cities(fake_id)
    city_id = cities["Vienna"]["id"]
    delete_result = {
        "type": "city",
        "id": city_id}
    database.delete(fake_id, delete_result)
    cities_after = database.show_cities(fake_id)
    assert cities_after == {}

def test_delete_country(test_db):
    fake_id = 1
    fake_result = {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "7.84719",
        "lon": "3.4583129670",
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save(fake_id, fake_result)
    countries = database.show_countries(fake_id)
    country_id = countries["Austria"]["id"]
    delete_result = {
        "type": "country",
        "id": country_id
    }
    database.delete(fake_id, delete_result)
    countries_after = database.show_countries(fake_id)
    cities_after = database.show_cities(fake_id)
    assert countries_after == {}
    assert cities_after == {}

def test_delete_country_with_multiple_cities(test_db):
    fake_id = 1
    vienna = {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "48.2082",
        "lon": "16.3738",
        "country_name": "Austria",
        "country_lat": "47.5162",
        "country_lon": "14.5501"}
    graz = {
        "city_name": "Graz",
        "addresstype": "city",
        "lat": "47.0707",
        "lon": "15.4395",
        "country_name": "Austria",
        "country_lat": "47.5162",
        "country_lon": "14.5501"}
    database.save(fake_id, vienna)
    database.save(fake_id, graz)
    countries = database.show_countries(fake_id)
    country_id = countries["Austria"]["id"]
    delete_result = {
        "type": "country",
        "id": country_id}
    database.delete(fake_id, delete_result)
    countries_after = database.show_countries(fake_id)
    cities_after = database.show_cities(fake_id)
    assert countries_after == {}
    assert cities_after == {}

def test_delete_nonexistent_city(test_db):
    fake_id = 1
    delete_result = {
        "type": "city",
        "id": 999}
    database.delete(fake_id, delete_result)
    cities = database.show_cities(fake_id)
    assert cities == {}

def test_delete_nonexistent_country(test_db):
    fake_id = 1
    delete_result = {
        "type": "country",
        "id": 999}
    database.delete(fake_id, delete_result)
    countries = database.show_countries(fake_id)
    cities = database.show_cities(fake_id)
    assert countries == {}
    assert cities == {}

def test_user_cannot_delete_another_users_country(test_db):
    fake_result = {
        "country_name": "Austria",
        "country_lat": "1.84719",
        "country_lon": "2.4583129670"}
    database.save_country(1, fake_result)
    countries = database.show_countries(1)
    country_id = countries["Austria"]["id"]
    delete_result = {
        "type": "country",
        "id": country_id}
    database.delete(2, delete_result)
    countries_after = database.show_countries(1)
    assert "Austria" in countries_after











    
#Tests for login and register
def test_register(test_db):
    username = "sasha"
    password = "12345"
    user_id = database.login(username, password, "register")
    assert user_id == 1


def test_register_existing_user(test_db):
    username = "sasha"
    password = "12345"
    database.login(username, password, "register")
    user_id = database.login(username, password, "register")
    assert user_id is None


def test_login(test_db):
    username = "sasha"
    password = "12345"
    database.login(username, password, "register")
    user_id = database.login(username, password, "login")
    assert user_id == 1


def test_login_wrong_password(test_db):
    username = "sasha"
    password = "12345"
    database.login(username, password, "register")
    user_id = database.login(username, "wrong_password", "login")
    assert user_id is None


def test_login_nonexistent_user(test_db):
    user_id = database.login("nonexistent", "12345", "login")
    assert user_id is None
    





