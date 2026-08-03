import sqlite3
from api import search

def save(user_id, result):
    db = sqlite3.connect("places.db")      # Подключаюсь к таблице
    c = db.cursor()

    c.execute("SELECT user_id, latitude, longitude FROM Visited_places WHERE user_id = ? AND latitude = ? AND longitude = ?",    
              (user_id, result["lat"], result["lon"]))      # Проверка, нет ли точно таких же записей, сравниваю по id пользователя и координатам                                 
    existing_place = c.fetchone()
    
    if existing_place == None:                             # Если совпадений нет, добавляю новую запись
        if result['addresstype'] == "city":
            c.execute(
                "INSERT INTO Visited_places VALUES(?, ?, ?, ?, ?)",
                (user_id, result["name"], result["country"], result["lat"], result["lon"]))           
        else:
            c.execute(
                "INSERT INTO Visited_places VALUES(?, ?, ?, ?, ?)",
                (user_id, None, result["name"], result["lat"], result["lon"]))

    db.commit()

    db.close()

result = search('Екатеринбург')
save(1, result)


db = sqlite3.connect("places.db")                              # код  для проверки
c = db.cursor()
c.execute("SELECT rowid, * FROM Visited_places")
print(c.fetchall())
db.close()

