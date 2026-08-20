import requests
from unittest.mock import Mock, patch

from backend.search_api import search_way, search_country, search

# Test search_way
@patch("backend.search_api.requests.get")
def test_search_way_success(mock_get):
    fake_response = Mock()
    fake_response.json.return_value = [
        {"name": "Vienna",
        "addresstype": "city"}]
    mock_get.return_value = fake_response
    result = search_way("Vienna")
    assert result == [
        {"name": "Vienna",
        "addresstype": "city"}]

@patch("backend.search_api.requests.get")
def test_search_way_request_error(mock_get):
    mock_get.side_effect = requests.RequestException
    result = search_way("Vienna")
    assert result == []


# Test search_country

@patch("backend.search_api.search_way")
def test_search_country_found(mock_search_way):
    mock_search_way.return_value = [
        {"name": "Vienna",
        "addresstype": "city",
        "lat": "48.208",
        "lon": "16.373"},
        {"name": "Austria",
        "addresstype": "country",
        "lat": "47.593",
        "lon": "14.124"}]
    result = search_country("Austria")
    assert result == {
        "country_name": "Austria",
        "country_lat": "47.593",
        "country_lon": "14.124"}

@patch("backend.search_api.requests.get")
def test_search_country_empty_response(mock_get):
    mock_get.return_value.json.return_value = []
    result = search_country("K")
    assert result is None


@patch("backend.search_api.search_way")
def test_search_country_not_found(mock_search_way):
    mock_search_way.return_value = [
        {"name": "Vienna",
        "addresstype": "city"}]
    result = search_country("Austria")
    assert result is None


# Test search
@patch("backend.search_api.search_country")
@patch("backend.search_api.search_way")
def test_search_city(mock_search_way, mock_search_country):
    mock_search_way.return_value = [
        {"name": "Vienna",
        "addresstype": "city",
        "lat": "48.208",
        "lon": "16.373",
        "address": {"country": "Austria"}}]
    mock_search_country.return_value = {
        "country_name": "Austria",
        "country_lat": "47.593",
        "country_lon": "14.124"}

    result = search("Vienna")
    assert result == {
        "city_name": "Vienna",
        "addresstype": "city",
        "lat": "48.208",
        "lon": "16.373",
        "country_name": "Austria",
        "country_lat": "47.593",
        "country_lon": "14.124"}


@patch("backend.search_api.search_country")
@patch("backend.search_api.search_way")
def test_search_country(mock_search_way, mock_search_country):
    mock_search_way.return_value = [
        {"name": "Austria",
        "addresstype": "country"}]
    mock_search_country.return_value = {
        "country_name": "Austria",
        "country_lat": "47.593",
        "country_lon": "14.124"}

    result = search("Austria")
    assert result == {
        "country_name": "Austria",
        "country_lat": "47.593",
        "country_lon": "14.124"}


@patch("backend.search_api.search_way")
def test_search_not_found(mock_search_way):
    mock_search_way.return_value = []
    result = search("asdasdasdasd")
    assert result is None



