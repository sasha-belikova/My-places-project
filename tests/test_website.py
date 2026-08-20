from unittest.mock import patch
from frontend.website import website


def test_start_redirects_to_home():
    client = website.test_client()
    response = client.get("/")
    assert response.status_code == 302
    assert response.location.endswith("/home/")


def test_home():
    client = website.test_client()
    response = client.get("/home/")
    assert response.status_code == 200


def test_my_home_without_login():
    client = website.test_client()
    response = client.get("/my_home")
    assert response.status_code == 302
    assert response.location.endswith("/home/")


@patch("frontend.website.login")
def test_login_success(mock_login):
    mock_login.return_value = 1
    client = website.test_client()
    response = client.post("/login/",data = {"username": "sasha", "password": "12345", "action": "login"})
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["user_id"] == 1


@patch("frontend.website.login")
def test_login_wrong_data(mock_login):
    mock_login.return_value = None
    client = website.test_client()
    response = client.post("/login/",data = {"username": "sasha", "password": "wrong", "action": "login"})
    assert response.status_code == 200
    assert response.data == b"ERROR"


@patch("frontend.website.search")
def test_search_box_not_found(mock_search):
    mock_search.return_value = None
    client = website.test_client()
    response = client.post("/search/", data = {"place": "A"})
    assert response.status_code == 200
    assert response.get_json() == {"Oops!": "No city or country like that! Please try again!"}


@patch("frontend.website.search")
def test_search_box_success(mock_search):
    mock_search.return_value = {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "12.5",
        "lon": "43"}
    client = website.test_client()
    response = client.post("/search/", data = {"place": "Vienna"})
    assert response.status_code == 200
    assert response.get_json() == mock_search.return_value


@patch("frontend.website.search")
def test_save_not_found(mock_search):
    mock_search.return_value = None
    client = website.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.post( "/save/",json = {"name": "A"})
    assert response.status_code == 200
    assert response.get_json() == {"found": False}


@patch("frontend.website.save")
@patch("frontend.website.search")
def test_save_success(mock_search, mock_save):
    mock_search.return_value = {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "6.56",
        "lon": "16.8",
        "country_name": "Austria",
        "country_lat": "42.5",
        "country_lon": "32.131"}
    client = website.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.post("/save/", json = {"name": "Vienna"})
    assert response.status_code == 200
    assert response.get_json() == {"found": True, "status": "saved", "type": "city", "country_name": "Austria"}
    mock_save.assert_called_once_with(1, mock_search.return_value)


@patch("frontend.website.delete")
def test_delete_place(mock_delete):
    client = website.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
    delete_data = {"type": "city", "id": 5}
    response = client.post("/delete/", json = delete_data)
    assert response.status_code == 200
    assert response.get_json() == {"success": True}
    mock_delete.assert_called_once_with(1, delete_data)