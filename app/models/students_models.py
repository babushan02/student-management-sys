from app.extensions import db
from app.utils import utc_now
from datetime import date


class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)

    enrollments = db.relationship(
        "Enrollment",
        backref="student",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "date_of_birth": self.date_of_birth.strftime("%Y-%m-%d")
        }

    def validate(self):
        errors = {}

        existing_student = Student.query.filter_by(
            student_id=self.student_id
        ).first()

        if (
            existing_student
            and existing_student.student_id != self.student_id
        ):
            errors["student_id"] = (
                "Student ID already exists"
            )

        if (
            not self.first_name.isalpha()
            or len(self.first_name) < 2
            or len(self.first_name) > 50
        ):
            errors["first_name"] = (
                "First name must contain only letters"
            )

        if (
            not self.last_name.isalpha()
            or len(self.last_name) < 2
            or len(self.last_name) > 50
        ):
            errors["last_name"] = (
                "Last name must contain only letters"
            )

        existing_student = Student.query.filter_by(
            email=self.email
        ).first()

        if (
            "@" not in self.email
            or "." not in self.email
            or (
                existing_student
                and existing_student.student_id != self.student_id
            )
        ):
            errors["email"] = (
                "Please enter a valid email address"
            )

        if self.date_of_birth >= date.today():
            errors["date_of_birth"] = (
                "Date of birth cannot be a future date"
            )

        return errors