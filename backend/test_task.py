import requests

gardens = requests.get("http://localhost:8000/api/gardens").json()
if not gardens:
    print("No gardens found")
    exit()

garden_id = gardens[0]["id"]
plants = requests.get(f"http://localhost:8000/api/gardens/{garden_id}/plants").json()
if not plants:
    print("No plants found")
    exit()

plant_id = plants[0]["id"]
print(f"Plant ID: {plant_id}")

tasks = requests.get(f"http://localhost:8000/api/plants/{plant_id}/tasks").json()
print("Initial tasks:")
for t in tasks.get("tasks", []):
    print(f"  {t['id']}: {t['completed']}")

task_id = tasks["tasks"][0]["id"]
print(f"Completing task {task_id}")
res = requests.post(f"http://localhost:8000/api/plants/{plant_id}/tasks/{task_id}")
print(f"Status: {res.status_code}")
print(f"Response: {res.json()}")

tasks = requests.get(f"http://localhost:8000/api/plants/{plant_id}/tasks").json()
print("Final tasks:")
for t in tasks.get("tasks", []):
    print(f"  {t['id']}: {t['completed']}")
