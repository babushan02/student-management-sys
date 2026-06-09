from app.extensions import db
from app.utils import utc_now
from datetime import date


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.course_id"), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "enrollment_id": self.enrollment_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrollment_date": self.enrollment_date.strftime("%Y-%m-%d"),
            "status": self.status
        }

    def validate(self):
        errors = {}

        existing_enrollment = Enrollment.query.filter_by(
            enrollment_id=self.enrollment_id
        ).first()

        if (
            existing_enrollment
            and existing_enrollment.enrollment_id != self.enrollment_id
        ):
            errors["enrollment_id"] = (
                "Enrollment ID already exists"
            )

        from app.models.students_models import Student

        student = Student.query.get(self.student_id)
        if not student:
            errors["student_id"] = (
                "Invalid student selected"
            )

        from app.models.courses_model import Course

        course = Course.query.get(self.course_id)
        if not course:
            errors["course_id"] = (
                "Invalid course selected"
            )

        if not self.enrollment_date:
            errors["enrollment_date"] = (
                "Enrollment date is required"
            )
        else:
            if self.enrollment_date > date.today():
                errors["enrollment_date"] = (
                    "Valid date required"
                )

        valid_status = ["Active", "Completed", "Dropped"]

        if (
            not self.status
            or self.status not in valid_status
        ):
            errors["status"] = (
                "Invalid enrollment status"
            )

        return errors