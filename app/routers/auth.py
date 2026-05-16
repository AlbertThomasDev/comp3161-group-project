from flask import Blueprint, request, jsonify, session
from app.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime


auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return generate_password_hash(password)

#Registered Users can login
@auth_bp.route("/login", methods=['POST'])
def login(): 
    db = get_db()
    cursor = db.cursor(dictionary=True)

    data = request.get_json()
    user_input_id = data.get("id")
    password = data.get("password")

    if not user_input_id or not password:
        return jsonify({"error": "ID and password required"}), 400

    #Check who is logging in
    if user_input_id.startswith("111"):  #Student
        role = "student"
        query = """
            SELECT u.user_id, u.user_password, u.user_role, u.user_name
            FROM Users u
            JOIN Students s ON u.user_id = s.user_id
            WHERE s.student_id = %s
        """
    elif user_input_id.startswith("222"): #Lecturer
        role = "lecturer"
        query = """
            SELECT u.user_id, u.user_password, u.user_role, u.user_name
            FROM Users u
            JOIN Lecturer_Course_Maintainers l ON u.user_id = l.user_id
            WHERE l.employee_id = %s
        """
    else:
        return jsonify({"error": "Invalid input"}), 400

    cursor.execute(query, (user_input_id,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "ID not found"}), 404

    #Verifying password
    if not check_password_hash(user["user_password"], password):
        return jsonify({"error": "Incorrect password"}), 401

    #Creating user session
    session["logged_in"] = True
    session["user_id"] = user["user_id"]  #created session incase frontend was created
    session["role"] = user["user_role"]

    return jsonify({
        "message": f"Welcome back {user['user_name']}!",
    }), 200
    
#Users can register
@auth_bp.route("/register", methods=['POST'])
def register():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        user_type = data.get("user_type")   # lecturer or student
        department = data.get("department")
        major = data.get("major")

        #validate role
        allowed = ("lecturer", "student", "admin")
        if user_type not in allowed:
            return jsonify({"error": f"User must be one of {allowed}"}), 400

        #hash password
        hashed_password = hash_password(password)  

        created_at = datetime.now()

        db.start_transaction()

        #Insert into Users table
        cursor.execute("""
            INSERT INTO Users (user_name, user_email, user_password, user_role, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, hashed_password, user_type, created_at))

        user_id = cursor.lastrowid #gets user_id

        #Generate role-based email
        short_id = str(user_id)[-4:]  #last digits of user_id

        if user_type == "lecturer":
            generated_email = f"lecturer{short_id}@school.com"
            cursor.execute("""
                UPDATE Users SET user_email = %s WHERE user_id = %s
            """, (generated_email, user_id))

            # generate lecturer employee_id
            cursor.execute("SELECT MAX(employee_id) AS max_id FROM Lecturer_Course_Maintainers")
            result = cursor.fetchone()
            prefix = "222"
            start_suffix = 1

            if result["max_id"]:
                last_id = str(result["max_id"])
                last_num = int(last_id[3:])
                new_num = last_num + 1
            else:
                new_num = start_suffix

            employee_id = f"{prefix}{new_num:06d}"

            cursor.execute("""
                INSERT INTO Lecturer_Course_Maintainers (employee_id, user_id, department)
                VALUES (%s, %s, %s)
            """, (employee_id, user_id, department))

        if user_type == "student": 
            generated_email = f"student{short_id}@school.com"
            cursor.execute("""
                UPDATE Users SET user_email = %s WHERE user_id = %s
            """, (generated_email, user_id))

            #generate student_id 
            cursor.execute("SELECT MAX(student_id) AS max_id FROM Students")
            result = cursor.fetchone()
            prefix = "111"
            start_suffix = 90001

            if result["max_id"]:
                last_id = str(result["max_id"])
                last_num = int(last_id[3:])
                new_num = last_num + 1
            else:
                new_num = start_suffix

            student_id = f"{prefix}{new_num:05d}"

            #Insert into student table
            cursor.execute("""
                INSERT INTO Students (student_id, user_id, major)
                VALUES (%s, %s, %s)
            """, (student_id, user_id, major))
        else:
            generated_email = f"admin{short_id}@school.com"
            cursor.execute("""
                UPDATE Users SET user_email = %s WHERE user_id = %s
            """, (generated_email, user_id))

            # generate lecturer admin_id
            cursor.execute("SELECT MAX(admin_id) AS max_id FROM Admin")
            result = cursor.fetchone()
            prefix = "333"
            start_suffix = 1

            if result["max_id"]:
                last_id = str(result["max_id"])
                last_num = int(last_id[3:])
                new_num = last_num + 1
            else:
                new_num = start_suffix

            admin_id = f"{prefix}{new_num:d}"

            access_level = 'high'

            #Insert into admin table
            cursor.execute("""
                INSERT INTO Admin (admin_id, user_id, access_level)
                VALUES (%s, %s, %s)
            """, (admin_id, user_id, access_level))

        db.commit()
        cursor.close()
        db.close()
        return jsonify({
            "message": f"You've successfully registered!",
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
