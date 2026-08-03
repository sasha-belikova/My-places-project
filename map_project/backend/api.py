import requests
def search(name):
    url = "https://nominatim.openstreetmap.org/search?"     # Сайт через который программа ищет координаты мест по названию

    headers = {'user-agent': 'map_project'}                 # Некоторая авторизация на сайте, чтобы не принимало за бота и не блокировало вызовы

    payload = {"q": name, "format": "json", "addressdetails": 1, "accept-language": "en"}    # решила выбрать именно формат свободной переменной,
                                                                    # потому что так, пользователь может ввести и город и страну, и даже и то и то,
                                                                    # и программа уже найдет самое ближайшее совпадение
                                                        
    r = requests.get(url, params = payload, headers = headers)  # делаем запрос на сайте

    coordinates = r.json()    # список, внутри которого лежит словарь с информацией о запрошенном месте

    if coordinates[0]['addresstype'] == "city":                           # Для городов, экстра возвращаю название страны, 
                                                                          # чтобы когда отмечаешь город не надо бвло снова отмечать страну
        info = {"name": coordinates[0]["name"],
        "country": coordinates[0]["address"]["country"],
        "addresstype": coordinates[0]["addresstype"],
        "lat": coordinates[0]["lat"],
        "lon": coordinates[0]["lon"]}
    else:
        info = {"name": coordinates[0]["name"],
        "addresstype": coordinates[0]["addresstype"],
        "lat": coordinates[0]["lat"],
        "lon": coordinates[0]["lon"]}     # возвращает название, широту, долготу

    return info

print(search("Россия"))






