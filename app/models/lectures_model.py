from app.extensions import db
from app.utils import utc_now
from datetime import date


class Lecturer(db.Model):
    __tablename__ = "lecturers"

    lecturer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "lecturer_id": self.lecturer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "department": self.department
        }

    def validate(self):
        errors = {}

        existing_lecturer = Lecturer.query.filter_by(
            lecturer_id=self.lecturer_id
        ).first()

        if (
            existing_lecturer
            and existing_lecturer.lecturer_id != self.lecturer_id
        ):
            errors["lecturer_id"] = (
                "Lecturer ID already exists"
            )

        if (
            not self.first_name
            or not self.first_name.isalpha()
        ):
            errors["first_name"] = (
                "Lecturer first name is required"
            )

        if (
            not self.last_name
            or not self.last_name.isalpha()
        ):
            errors["last_name"] = (
                "Lecturer last name is required"
            )

        existing_email = Lecturer.query.filter_by(
            email=self.email
        ).first()

        if (
            "@" not in self.email
            or "." not in self.email
            or (
                existing_email
                and existing_email.lecturer_id != self.lecturer_id
            )
        ):
            errors["email"] = (
                "Invalid lecturer email address"
            )

        if not self.department or self.department.strip() == "":
            errors["department"] = (
                "Department is required"
            )

        return errors