import requests
def search_way(name):
    url = "https://nominatim.openstreetmap.org/search?"     
    headers = {'user-agent': 'map_project'}                 
    payload = {"q": name, "format": "json", "addressdetails": 1, "accept-language": "en"}    
                                                                        
                                                            
    r = requests.get(url, params = payload, headers = headers)  
    return r.json()

def search_country(name):
    coordinates = search_way(name)
    for place in coordinates:
        if place["addresstype"] == "country":
            info_country = {"country_name": place["name"],
                "country_lat": place["lat"],
                "country_lon": place["lon"]}
    return info_country

def search(name):
    coordinates = search_way(name)
    if coordinates == []:
        return None
    for place in coordinates:
        if place["addresstype"] in ["city", "town", "village", "province"]:                                                                                     # чтобы когда отмечаешь город не надо бвло снова отмечать страну
            info = {"city_name": coordinates[0]["name"],
            "addresstype": coordinates[0]["addresstype"],
            "lat": coordinates[0]["lat"],
            "lon": coordinates[0]["lon"]}

            return info | search_country(coordinates[0]["address"]["country"]) 

        elif place['addresstype'] == "country":
            return search_country(name)

    else:
        return None

