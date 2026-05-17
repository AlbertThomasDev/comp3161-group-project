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
    elif user_input_id.startswith("333"):  # Admin
        role = "admin"
        query = """
            SELECT u.user_id, u.user_password, u.user_role, u.user_name
            FROM Users u
            JOIN admins a ON u.user_id = a.user_id
            WHERE a.admin_id = %s
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
        "role": user["user_role"],
    }), 200
    
#Users can register
@auth_bp.route("/register", methods=['POST'])
def register():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        data = request.get_json()

        name = data.get("name")
        password = data.get("password")
        user_type = data.get("user_type")
        department = data.get("department")
        major = data.get("major")

        allowed = ("lecturer", "student", "admin")
        if user_type not in allowed:
            return jsonify({"error": f"User must be one of {allowed}"}), 400

        hashed_password = hash_password(password)
        created_at = datetime.now()

        db.start_transaction()

        cursor.execute("""
            INSERT INTO Users (user_name, user_email, user_password, user_role, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, "placeholder", hashed_password, user_type, created_at))

        user_id = cursor.lastrowid
        short_id = str(user_id)[-4:]

        if user_type == "lecturer":
            generated_email = f"lecturer{short_id}@school.com"
            cursor.execute("UPDATE Users SET user_email = %s WHERE user_id = %s", (generated_email, user_id))
            cursor.fetchall()  # consume update results

            cursor.execute("SELECT MAX(CAST(SUBSTRING(employee_id, 4) AS UNSIGNED)) AS max_num FROM Lecturer_Course_Maintainers")
            result = cursor.fetchone()

            new_num = (result["max_num"] + 1) if result["max_num"] else 1
            employee_id = f"222{new_num:06d}"

            cursor.execute("""
                INSERT INTO Lecturer_Course_Maintainers (employee_id, user_id, department)
                VALUES (%s, %s, %s)
            """, (employee_id, user_id, department))
            cursor.fetchall()

            db.commit()
            return jsonify({
                "message": "You've successfully registered!",
                "employee_id": employee_id,
                "role": user_type
            }), 201

        elif user_type == "student":
            generated_email = f"student{short_id}@school.com"
            cursor.execute("UPDATE Users SET user_email = %s WHERE user_id = %s", (generated_email, user_id))
            cursor.fetchall()  # consume update results

            cursor.execute("SELECT MAX(CAST(SUBSTRING(student_id, 4) AS UNSIGNED)) AS max_num FROM Students")
            result = cursor.fetchone()

            new_num = (result["max_num"] + 1) if result["max_num"] else 90001
            student_id = f"111{new_num:05d}"

            cursor.execute("""
                INSERT INTO Students (student_id, user_id, major)
                VALUES (%s, %s, %s)
            """, (student_id, user_id, major))
            cursor.fetchall()

            db.commit()
            return jsonify({
                "message": "You've successfully registered!",
                "student_id": student_id,
                "role": user_type
            }), 201

        else:  # admin
            print("REACHED ADMIN BRANCH")
            generated_email = f"admin{short_id}@school.com"
            cursor.execute("UPDATE Users SET user_email = %s WHERE user_id = %s", (generated_email, user_id))
            cursor.fetchall()  # consume update results

            cursor.execute("SELECT MAX(CAST(SUBSTRING(admin_id, 4) AS UNSIGNED)) AS max_num FROM admins")
            result = cursor.fetchone()
            print(f"MAX RESULT: {result}")

            new_num = (result["max_num"] + 1) if result["max_num"] else 1
            admin_id = f"333{new_num:06d}"
            print(f"GENERATED ADMIN ID: {admin_id}")

            cursor.execute("""
                INSERT INTO admins (admin_id, user_id, access_level)
                VALUES (%s, %s, %s)
            """, (admin_id, user_id, "high"))
            cursor.fetchall()
            print("ADMIN INSERT DONE")

            db.commit()
            return jsonify({
                "message": "You've successfully registered!",
                "admin_id": admin_id,
                "role": user_type
            }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

    """
    Fixed admin and lecturer table not being filled after a new user
    is created. 
    """