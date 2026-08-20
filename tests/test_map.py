from unittest.mock import patch
import folium
from frontend.map import build_map, noId_build_map


@patch("frontend.map.show_cities")
@patch("frontend.map.countries_borders")
def test_build_map_empty(mock_countries_borders, mock_show_cities):
    mock_countries_borders.return_value = folium.FeatureGroup()
    mock_show_cities.return_value = {}
    result = build_map(1)
    m, countries_layer_name, city_layer_name = result
    assert isinstance(m, folium.Map)
    assert isinstance(countries_layer_name, str)
    assert isinstance(city_layer_name, str)


@patch("frontend.map.show_cities")
@patch("frontend.map.countries_borders")
def test_build_map_with_cities(mock_countries_borders, mock_show_cities):
    mock_countries_borders.return_value = folium.FeatureGroup()
    mock_show_cities.return_value = {
        "Vienna": {
            "id": 1,
            "latitude": 1.2082,
            "longitude": 2.3738},
        "Graz": {
            "id": 2,
            "latitude": 4.0707,
            "longitude": 7.4395}}
    m, countries_layer_name, city_layer_name = build_map(1)
    html = m._repr_html_()
    assert "Vienna" in html
    assert "Graz" in html


@patch("frontend.map.show_cities")
@patch("frontend.map.countries_borders")
def test_build_map_calls_functions_with_user_id(mock_countries_borders, mock_show_cities):
    mock_countries_borders.return_value = folium.FeatureGroup()
    mock_show_cities.return_value = {}
    build_map(42)
    mock_countries_borders.assert_called_once_with(42)
    mock_show_cities.assert_called_once_with(42)


@patch("frontend.map.show_cities")
@patch("frontend.map.countries_borders")
def test_build_map_multiple_cities(mock_countries_borders, mock_show_cities):
    mock_countries_borders.return_value = folium.FeatureGroup()
    mock_show_cities.return_value = {
        "Vienna": {
            "id": 1,
            "latitude": 1.2082,
            "longitude": 2.3738},
        "Berlin": {
            "id": 2,
            "latitude": 3.5200,
            "longitude": 4.4050},
        "Paris": {
            "id": 3,
            "latitude": 5.8566,
            "longitude": 6.3522}}
    m, countries_layer_name, city_layer_name = build_map(1)
    html = m._repr_html_()
    assert "Vienna" in html
    assert "Berlin" in html
    assert "Paris" in html


def test_noId_build_map():
    result = noId_build_map()
    assert isinstance(result, folium.Map)


def test_noId_build_map_location():
    result = noId_build_map()
    assert result.location == [0, 0]
    assert result.options["zoom"] == 3


def test_noId_build_map_has_controls():
    result = noId_build_map()
    html = result._repr_html_()
    assert "MiniMap" in html