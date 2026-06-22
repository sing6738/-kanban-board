import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Task

app = Flask(__name__, static_folder=".")
CORS(app)

# ── Database URL ──────────────────────────────────────────────────────────────
# Render (and older Heroku) provide "postgres://" but SQLAlchemy 1.4+ requires
# "postgresql://".  This one-liner fixes it transparently.
raw_url = os.environ.get("DATABASE_URL", "sqlite:///kanban.db")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = raw_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables on first run (safe to call repeatedly)
with app.app_context():
    db.create_all()


# ── Serve the frontend ────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# ── GET /tasks ────────────────────────────────────────────────────────────────
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.order_by(Task.id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


# ── POST /tasks ───────────────────────────────────────────────────────────────
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    task_name = (data.get("task_name") or "").strip()
    subject = (data.get("subject") or "").strip()

    if not task_name:
        return jsonify({"error": "task_name is required"}), 422

    task = Task(task_name=task_name, subject=subject)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


# ── PUT /tasks/<id> ───────────────────────────────────────────────────────────
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json(silent=True) or {}

    if "task_name" in data and data["task_name"].strip():
        task.task_name = data["task_name"].strip()
    if "subject" in data:
        task.subject = data["subject"].strip()
    if "status" in data:
        if data["status"] not in ("todo", "done"):
            return jsonify({"error": "status must be 'todo' or 'done'"}), 422
        task.status = data["status"]

    db.session.commit()
    return jsonify(task.to_dict()), 200


# ── DELETE /tasks/<id> ────────────────────────────────────────────────────────
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Task {task_id} deleted"}), 200


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
