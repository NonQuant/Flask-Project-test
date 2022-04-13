from requests import delete, get, post


# тестировка получения всех работ
print(get("http://localhost:5000/api/v2/jobs").json())

# пустой запрос на создание работы
print(post("http://localhost:5000/api/v2/jobs").json())

# некорректный запрос на создание работы
print(post("http://localhost:5000/api/v2/jobs", json={
    "job": "dfskadjkasd"
}).json())

# корректные запросы на создание работы
print(post("http://localhost:5000/api/v2/jobs", json={
    "team_leader": 1,
    "job": "Fixing a main door",
    "work_size": 3,
    "collaborators": "1, 2",
    "is_finished": False,
}).json())

print(post("http://localhost:5000/api/v2/jobs", json={
    "team_leader": 1,
    "job": "Fixing a second door",
    "work_size": 1,
    "collaborators": "1",
    "is_finished": True,
}).json())

# запрос на получение несуществующей работы
print(get("http://localhost:5000/api/v2/jobs/999").json())

# корректный запрос на получение работы
print(get("http://localhost:5000/api/v2/jobs/1").json())

# запрос на удаление несуществующей работы
print(delete("http://localhost:5000/api/v2/jobs/4312").json())

# корректный запрос на удаление работы
print(delete("http://localhost:5000/api/v2/jobs/2").json())

# получение всех работ для проверки изменений
print(get("http://localhost:5000/api/v2/jobs").json())