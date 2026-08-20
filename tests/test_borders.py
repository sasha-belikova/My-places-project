from unittest.mock import patch

from backend.borders import all_countries, countries_borders


def test_all_countries_returns_geojson():
    result = all_countries()
    assert isinstance(result, type(all_countries()))


def test_all_countries_contains_geojson():
    result = all_countries()
    assert result.data["type"] == "FeatureCollection"
    assert "features" in result.data


@patch("backend.borders.show_countries")
def test_countries_borders_returns_chosen_country(mock_show_countries):
    mock_show_countries.return_value = {
        "Austria": {
            "id": 1,
            "latitude": 47.5,
            "longitude": 14.5}}
    result = countries_borders(1)
    assert result.data["type"] == "FeatureCollection"
    assert len(result.data["features"]) == 1
    assert result.data["features"][0]["properties"]["NAME"] == "Austria"


@patch("backend.borders.show_countries")
def test_countries_borders_returns_empty_when_no_countries(mock_show_countries):
    mock_show_countries.return_value = {}
    result = countries_borders(1)
    assert result.data["type"] == "FeatureCollection"
    assert result.data["features"] == []


@patch("backend.borders.show_countries")
def test_countries_borders_does_not_include_unselected_countries(mock_show_countries):
    mock_show_countries.return_value = {
        "Austria": {
            "id": 1,
            "latitude": 47.5,
            "longitude": 14.5}}
    result = countries_borders(1)
    country_names = [
        feature["properties"]["NAME"]
        for feature in result.data["features"]]
    assert "Austria" in country_names
    assert "Germany" not in country_names

@patch("backend.borders.show_countries")
def test_countries_borders_multiple_countries(mock_show_countries):
    mock_show_countries.return_value = {
        "Austria": {
            "id": 1,
            "latitude": 47.5,
            "longitude": 14.5},
        "Germany": {
            "id": 2,
            "latitude": 51.1,
            "longitude": 10.4}}
    result = countries_borders(1)
    country_names = [
        feature["properties"]["NAME"]
        for feature in result.data["features"]]
    assert "Austria" in country_names
    assert "Germany" in country_names
    assert len(country_names) == 2

@patch("backend.borders.show_countries")
def test_countries_borders_unknown_user(mock_show_countries):
    mock_show_countries.return_value = {}
    result = countries_borders(999999)
    assert result.data["features"] == []

@patch("backend.borders.show_countries")
def test_countries_borders_country_not_in_geojson(mock_show_countries):
    mock_show_countries.return_value = {
        "A": {
            "id": 1,
            "latitude": 0,
            "longitude": 0}}
    result = countries_borders(1)
    assert result.data["type"] == "FeatureCollection"
    assert result.data["features"] == []