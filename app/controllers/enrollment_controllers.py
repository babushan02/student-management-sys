from flask import jsonify, request

from app.extensions import db
from app.models.enrollment_model import Enrollment

def _validate_enrollment_payload(data, enrollment_id=None):
    errors = []

    if not data:
        return ["Request body is required."]

    student_id = data.get("student_id")
    if not student_id:
        errors.append("Invalid student selected")
    else:
        from app.models.students_models import Student
        student = Student.query.get(student_id)
        if not student:
            errors.append("Invalid student selected")

    course_id = data.get("course_id")
    if not course_id:
        errors.append("Invalid course selected")
    else:
        from app.models.courses_model import Course
        course = Course.query.get(course_id)
        if not course:
            errors.append("Invalid course selected")

    enrollment_date = data.get("enrollment_date")
    if not enrollment_date:
        errors.append("Enrollment date is required")
    else:
        try:
            from datetime import date
            parsed_date = date.fromisoformat(enrollment_date)
            if parsed_date > date.today():
                errors.append("Valid date required")
        except ValueError:
            errors.append("Valid date required")

    status = data.get("status")
    valid_status = ["Active", "Completed", "Dropped"]

    if not status or status not in valid_status:
        errors.append("Invalid enrollment status")

    return errors

def create_enrollment():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required."}), 400

    errors = _validate_enrollment_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        from datetime import date

        enrollment = Enrollment(
            student_id=int(data.get("student_id")),
            course_id=int(data.get("course_id")),
            enrollment_date=date.fromisoformat(data.get("enrollment_date")),
            status=data.get("status").strip()
        )

        db.session.add(enrollment)
        db.session.commit()

        return jsonify({
            "message": "Enrollment created successfully.",
            "enrollment": enrollment.to_dict()
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

def get_enrollments():
    enrollments = Enrollment.query.all()

    return jsonify({
        "enrollments": [e.to_dict() for e in enrollments]
    }), 200

def get_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404

    return jsonify({
        "enrollment": enrollment.to_dict()
    }), 200

def update_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No data provided"}), 400

    errors = _validate_enrollment_payload(data, enrollment_id=enrollment_id)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        from datetime import date

        enrollment.student_id = int(data.get("student_id", enrollment.student_id))
        enrollment.course_id = int(data.get("course_id", enrollment.course_id))

        if "enrollment_date" in data:
            enrollment.enrollment_date = date.fromisoformat(data.get("enrollment_date"))

        enrollment.status = data.get("status", enrollment.status).strip()

        db.session.commit()

        return jsonify({
            "message": "Enrollment updated successfully.",
            "enrollment": enrollment.to_dict()
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404

    try:
        db.session.delete(enrollment)
        db.session.commit()

        return jsonify({
            "message": "Enrollment deleted successfully"
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500