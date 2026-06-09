from datetime import date

from flask import jsonify, request

from app.extensions import db
from app.models.students_models import Student


def _validate_student_payload(data, student_id=None):
    errors = []

    if not data:
        return ["Request body is required."]

    first_name = data.get("first_name")
    if not first_name or str(first_name).strip() == "":
        errors.append("first_name is required.")

    last_name = data.get("last_name")
    if not last_name or str(last_name).strip() == "":
        errors.append("last_name is required.")

    email = data.get("email")
    if not email or str(email).strip() == "":
        errors.append("email is required.")
    else:
        q = Student.query.filter(Student.email == str(email).strip())
        if student_id:
            q = q.filter(Student.student_id != student_id)
        if q.first():
            errors.append("Email address already exists.")

    dob = data.get("date_of_birth")
    if not dob:
        errors.append("date_of_birth is required.")
    else:
        try:
            dob_date = date.fromisoformat(dob)
            if dob_date >= date.today():
                errors.append("Date of birth cannot be a future date.")
        except ValueError:
            errors.append("date_of_birth must be in YYYY-MM-DD format.")

    return errors

def create_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required."}), 400

    errors = _validate_student_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        student = Student(
            first_name=data.get("first_name").strip(),
            last_name=data.get("last_name").strip(),
            email=data.get("email").strip(),
            date_of_birth=date.fromisoformat(data.get("date_of_birth"))
        )

        db.session.add(student)
        db.session.commit()

        return jsonify({
            "message": "Student created successfully.",
            "student": student.to_dict()
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

def get_students():
    students = Student.query.all()
    return jsonify({
        "students": [s.to_dict() for s in students]
    }), 200

def get_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"student": student.to_dict()}), 200

def update_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No data provided"}), 400

    errors = _validate_student_payload(data, student_id=student_id)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        student.first_name = data.get("first_name", student.first_name).strip()
        student.last_name = data.get("last_name", student.last_name).strip()
        student.email = data.get("email", student.email).strip()

        if "date_of_birth" in data:
            student.date_of_birth = date.fromisoformat(data.get("date_of_birth"))

        db.session.commit()

        return jsonify({
            "message": "Student updated successfully.",
            "student": student.to_dict()
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

def delete_student(student_id):
    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    try:
        db.session.delete(student)
        db.session.commit()

        return jsonify({"message": "Student deleted successfully"}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500