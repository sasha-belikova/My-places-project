import requests
def search_way(name):
    url = "https://nominatim.openstreetmap.org/search?"     
    headers = {'user-agent': 'map_project'}                 
    payload = {"q": name, "format": "json", "addressdetails": 1, "accept-language": "en"}                                                                       
    try:
        r = requests.get(url, params = payload, headers = headers, timeout = 10)
        return r.json()
    except requests.RequestException:
        return []

def search_country(name):
    coordinates = search_way(name)
    for place in coordinates:
        if place["addresstype"] == "country":
            info_country = {
                "country_name": place["name"],
                "country_lat": place["lat"],
                "country_lon": place["lon"]}
            return info_country
    return None
    

def search(name):
    coordinates = search_way(name)
    if coordinates == []:
        return None
    for place in coordinates:
        if place["addresstype"] in ["city", "town", "village", "province"]:                                                                                     # чтобы когда отмечаешь город не надо бвло снова отмечать страну
            info = {"city_name": place["name"],
            "addresstype": place["addresstype"],
            "lat": place["lat"],
            "lon": place["lon"]}

            return info | search_country(place["address"]["country"]) 

        elif place["addresstype"] == "country":
            return search_country(name)

    else:
        return None

