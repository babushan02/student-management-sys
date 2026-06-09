from flask import jsonify, request

from app.extensions import db
from app.models.lectures_model import Lecturer

def _validate_lecturer_payload(data, lecturer_id=None):
    errors = []

    if not data:
        return ["Request body is required."]

    first_name = data.get("first_name")
    if not first_name or str(first_name).strip() == "":
        errors.append("Lecturer first name is required.")
    elif not str(first_name).isalpha():
        errors.append("Lecturer first name is required.")

    last_name = data.get("last_name")
    if not last_name or str(last_name).strip() == "":
        errors.append("Lecturer last name is required.")
    elif not str(last_name).isalpha():
        errors.append("Lecturer last name is required.")

    email = data.get("email")
    if not email or str(email).strip() == "":
        errors.append("Invalid lecturer email address")
    else:
        q = Lecturer.query.filter(Lecturer.email == str(email).strip())
        if lecturer_id:
            q = q.filter(Lecturer.lecturer_id != lecturer_id)
        if q.first():
            errors.append("Lecturer ID already exists")

    department = data.get("department")
    if not department or str(department).strip() == "":
        errors.append("Department is required")

    return errors

def create_lecturer():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    errors = _validate_lecturer_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        lecturer = Lecturer(
            first_name=data.get("first_name").strip(),
            last_name=data.get("last_name").strip(),
            email=data.get("email").strip(),
            department=data.get("department").strip()
        )

        db.session.add(lecturer)
        db.session.commit()

        return jsonify({
            "message": "Lecturer created successfully.",
            "lecturer": lecturer.to_dict()
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def get_lecturers():
    lecturers = Lecturer.query.all()

    return jsonify({
        "lecturers": [l.to_dict() for l in lecturers]
    }), 200

def get_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)

    if not lecturer:
        return jsonify({"error": "Lecturer not found."}), 404

    return jsonify({"lecturer": lecturer.to_dict()}), 200

def update_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)

    if not lecturer:
        return jsonify({"error": "Lecturer not found."}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No data provided to update."}), 400

    errors = _validate_lecturer_payload(data, lecturer_id=lecturer_id)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        lecturer.first_name = data.get("first_name", lecturer.first_name).strip()
        lecturer.last_name = data.get("last_name", lecturer.last_name).strip()
        lecturer.email = data.get("email", lecturer.email).strip()
        lecturer.department = data.get("department", lecturer.department).strip()

        db.session.commit()

        return jsonify({
            "message": "Lecturer updated successfully.",
            "lecturer": lecturer.to_dict()
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500

def delete_lecturer(lecturer_id):
    lecturer = Lecturer.query.get(lecturer_id)

    if not lecturer:
        return jsonify({"error": "Lecturer not found."}), 404

    try:
        db.session.delete(lecturer)
        db.session.commit()

        return jsonify({"message": "Lecturer deleted successfully."}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500