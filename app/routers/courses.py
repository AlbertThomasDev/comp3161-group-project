from flask import Blueprint, jsonify
from db import get_db

courses_bp = Blueprint('courses', __name__)

# Get all courses
@courses_bp.route('/', methods=['GET'])
def get_courses():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT course_id, course_code, course_name, course_description,
               semester_number, semester_year, employee_id
        FROM Course
    """)

    courses = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(courses)


# Get a single course
@courses_bp.route('/<int:course_id>', methods=['GET'])
def get_course(course_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM Course
        WHERE course_id = %s
    """, (course_id,))

    course = cursor.fetchone()

    cursor.close()
    db.close()

    if course:
        return jsonify(course)

    return jsonify({"error": "Course not found"}), 404


# Get courses a student is enrolled in
@courses_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_courses(student_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.course_code
        FROM Enrolled_In e
        JOIN Course c ON e.course_id = c.course_id
        WHERE e.student_id = %s
    """, (student_id,))

    courses = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(courses)
