from app.extensions import db
from app.utils import utc_now


class Course(db.Model):
    __tablename__ = "courses"

    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("lecturers.lecturer_id"), nullable=False)

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "course_code": self.course_code,
            "course_name": self.course_name,
            "credits": self.credits,
            "lecturer_id": self.lecturer_id
        }

    def validate(self):
        errors = {}

        existing_course = Course.query.filter_by(
            course_id=self.course_id
        ).first()

        if (
            existing_course
            and existing_course.course_id != self.course_id
        ):
            errors["course_id"] = (
                "Course ID already exists"
            )

        existing_code = Course.query.filter_by(
            course_code=self.course_code
        ).first()

        if existing_code and existing_code.course_id != self.course_id:
            errors["course_code"] = (
                "Course code already exists"
            )

        if (
            not self.course_name
            or len(self.course_name.strip()) < 3
        ):
            errors["course_name"] = (
                "Course name is required"
            )

        if (
            self.credits is None
            or not isinstance(self.credits, int)
            or self.credits < 1
            or self.credits > 6
        ):
            errors["credits"] = (
                "Credits must be between 1 and 6"
            )

        from app.models.lectures_model import Lecturer

        lecturer = Lecturer.query.get(self.lecturer_id)
        if not lecturer:
            errors["lecturer_id"] = (
                "Invalid lecturer selected"
            )

        return errors