from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200), nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="todo")

    def to_dict(self):
        return {
            "id": self.id,
            "task_name": self.task_name,
            "subject": self.subject,
            "status": self.status,
        }
