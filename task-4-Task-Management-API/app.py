
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Install Docker", "completed": True},
    {"id": 2, "title": "Build Docker Image", "completed": False}
]

next_id = 3

@app.route("/")
def home():
    return jsonify(message="Task Management API")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks=tasks)

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            return jsonify(task)

    abort(404, description="Task not found")

@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return jsonify(error="Task title is required"), 400

    task = {
        "id": next_id,
        "title": title.strip(),
        "completed": False
    }

    tasks.append(task)
    next_id += 1

    return jsonify(task), 201

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return "", 204

    abort(404, description="Task not found")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

