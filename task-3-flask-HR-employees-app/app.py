
from flask import Flask, jsonify, abort

app = Flask(__name__)

employees = [
    {"id": 1, "name": "Ahmed", "department": "DevOps"},
    {"id": 2, "name": "Mohamed", "department": "Front-End"},
    {"id": 3, "name": "Mahmoud", "department": "cloud"},
    {"id": 4, "name": "Yara", "department": "Platform"},
    {"id": 5, "name": "Lamiaa", "department": "Back-End"}
]

@app.route("/")
def home():
    return jsonify(message="Employee API is running")

@app.route("/employees")
def get_employees():
    return jsonify(employees=employees)

@app.route("/employees/<int:employee_id>")
def get_employee(employee_id):
    for employee in employees:
        if employee["id"] == employee_id:
            return jsonify(employee)

    abort(404, description="Employee not found")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

