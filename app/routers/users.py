#route/users.py
#for users/members
#file should handle getting all users. getting single users, getting lecturers, and getting students 

from flask import Blueprint, jsonify #necessary import 
from db import get_db #necessary import 

users_bp = Blueprint('users', __name__)

#get all users 
@users_bp.route('/', methods=['GET'])
def get_all_users():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT user_id, user_name, user_email, user_role
        FROM Users
    """)

    users = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(users) 

#get a single user 
@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT user_id, user_name, user_email, user_role
        FROM Users
        WHERE user_id = %s
    """, (user_id,))

    user = cursor.fetchone()

    cursor.close()
    db.close()

    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404 

#get all students 
@users_bp.route('/students', methods=['GET'])
def get_students():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.student_id, u.user_name, u.user_email, s.major
        FROM Students s
        JOIN Users u ON s.user_id = u.user_id
    """)

    students = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(students) 

#get all lecturers
@users_bp.route('/lecturers', methods=['GET'])
def get_lecturers():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT l.employee_id, u.user_name, u.user_email, l.department
        FROM Lecturer_Course_Maintainers l
        JOIN Users u ON l.user_id = u.user_id
    """)

    lecturers = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(lecturers)
