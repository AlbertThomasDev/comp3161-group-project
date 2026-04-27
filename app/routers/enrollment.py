#routers/enrollment
#route to handle getting courses for a student, getting members of a course, and enrolling a student 

from flask import Blueprint, requests, jsonify #necessary import
from db import get_db #necessary import

enrollment_bp = Blueprint('enrollment', __name__)

#enroll a student in course
@enrollment_bp.route('/enroll', methods=['POST'])
def enroll_student():
    data = request.get_json()

    student_id = data.get('student_id')
    course_id = data.get('course_id')

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO Enrolled_In (student_id, course_id, date_enrolled, enroll_status)
            VALUES (%s, %s, CURDATE(), 'enrolled')
        """, (student_id, course_id))

        db.commit()
        return jsonify({"message": "Student enrolled successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        db.close() 

#get members of a course 
@enrollment_bp.route('/course/<int:course_id>/members', methods=['GET'])
def get_course_members(course_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.student_id, u.user_name, u.user_email
        FROM Enrolled_In e
        JOIN Students s ON e.student_id = s.student_id
        JOIN Users u ON s.user_id = u.user_id
        WHERE e.course_id = %s
    """, (course_id,))

    members = cursor.fetchall()

    cursor.close()
    db.close() 
    return jsonify(members)
