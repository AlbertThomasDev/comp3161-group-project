from flask import Blueprint, request, jsonify, session, send_file
from app.database import get_db
import os

assignments_bp = Blueprint('assignments', __name__)

#Submit an assignment
@assignments_bp.route("/submit_assignment", methods=['POST'])
def submit_assignment():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if "user_id" not in session:
        return jsonify({"error":"Not logged in"}), 401

    user_id = session["user_id"]

    cursor.execute(
        """ SELECT student_id FROM Students WHERE user_id = %s """, (user_id,)
    )
    sdt = cursor.fetchone()
    cursor.fetchall()
    student_id = sdt["student_id"]

    course_name = request.form.get("course_name")
    assignment_name = request.form.get("assignment_name")
    link = request.form.get("link")
    file = request.files.get("file")

    if not course_name or not assignment_name:
        return jsonify({"error":"Course or Assignment name are required"}), 400

    # Handle file or link first
    if file:
        upload_folder = os.path.join(os.getcwd(), "uploads")
        os.makedirs(upload_folder, exist_ok=True)
        filename = file.filename
        file.save(os.path.join(upload_folder, filename))
        file_path = f"uploads/{filename}"
    elif link:
        file_path = link
    else:
        return jsonify({"error":"No file or link submitted"}), 400

    cursor.execute("""
        SELECT course_id FROM Course WHERE course_name = %s
    """, (course_name,))
    course = cursor.fetchone()
    cursor.fetchall()
    if not course:
        return jsonify({"error":"Course not found"}), 400
    course_id = course["course_id"]

    cursor.execute("""
        SELECT * FROM Enrolled_In WHERE student_id = %s AND course_id = %s""",
        (student_id, course_id))
    if not cursor.fetchone():
        return jsonify({"error":"You're not enrolled in this course"}), 403
    cursor.fetchall()

    cursor.execute("""
        SELECT assignment_id FROM Assignment WHERE course_id = %s AND title = %s
    """, (course_id, assignment_name))
    assignment = cursor.fetchone()
    cursor.fetchall()
    if not assignment:
        return jsonify({"error":"Assignment not found"}), 404
    assignment_id = assignment["assignment_id"]

    cursor.execute("""
        SELECT submission_id FROM Submission
        WHERE student_id = %s AND assignment_id = %s
    """, (student_id, assignment_id))
    exist = cursor.fetchone()
    cursor.fetchall()

    if exist:
        cursor.execute("""
            UPDATE Submission SET file_path = %s, submission_date = NOW()
            WHERE submission_id = %s
        """, (file_path, exist["submission_id"]))
    else:
        cursor.execute("""
            INSERT INTO Submission (assignment_id, student_id, submission_date, file_path) 
            VALUES (%s, %s, NOW(), %s)
        """, (assignment_id, student_id, file_path))

    db.commit()
    return jsonify({"message":"Assignment submitted"}), 201

#If Lecturer teaches a course
def lec_teaches(cursor, lecturer_id, course_id):
    cursor.execute("""
        SELECT * FROM Course 
        WHERE employee_id = %s AND course_id = %s""", (lecturer_id, course_id))
    result = cursor.fetchone()
    cursor.fetchall()  # consume remaining results
    return result is not None


#Lecturers can view submissions for assignments
@assignments_bp.route("/submissions/<string:title>", methods=['GET'])
def view_assignments(title):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if "user_id" not in session:
        return jsonify({"error":"Not logged in"}), 401

    user_id = session["user_id"]

    #Get lecturer
    cursor.execute(
        """ SELECT employee_id FROM Lecturer_Course_Maintainers WHERE user_id = %s """, (user_id,)
    )
    lec = cursor.fetchone()
    cursor.fetchall()

    lecturer_id = lec["employee_id"]

    #Get the course for the assignment
    cursor.execute("""
        SELECT assignment_id, course_id FROM Assignment 
        WHERE title = %s AND course_id IN (
            SELECT course_id FROM Course WHERE employee_id = %s
        )
    """, (title, lecturer_id))
    assignment = cursor.fetchone()
    cursor.fetchall()

    if not assignment:
        return jsonify({"error":"Assignment not found"}),404

    course_id = assignment["course_id"]
    assignment_id = assignment["assignment_id"]

    # print(f"lecturer_id: {lecturer_id}")
    # print(f"course_id: {course_id}")

    #check if lecturer teaches course
    if not lec_teaches(cursor,lecturer_id,course_id):
        return jsonify({"error":"Unauthorized - Not a lecturer of this course"}), 403
    
    cursor.execute("""
        SELECT submission_id, student_id, grade, submission_date
        FROM Submission 
        WHERE assignment_id = %s
    """,(assignment_id,))

    submissions = cursor.fetchall()
    return jsonify(submissions), 200

#Download the assignment for a specific student
@assignments_bp.route("/submissions/<int:student_id>/download/<int:assignment_id>", methods=['GET'])
def download_assignments(student_id, assignment_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if "user_id" not in session:
        return jsonify({"error":"Not logged in"}), 401

    user_id = session["user_id"]

    cursor.execute(
        """ SELECT employee_id FROM Lecturer_Course_Maintainers WHERE user_id = %s """, (user_id,)
    )
    lec = cursor.fetchone()
    cursor.fetchall()

    lecturer_id = lec["employee_id"]

    # Get the specific submission
    cursor.execute("""
        SELECT s.file_path, a.course_id
        FROM Submission s
        JOIN Assignment a ON a.assignment_id = s.assignment_id
        WHERE s.student_id = %s AND s.assignment_id = %s
    """, (student_id, assignment_id))
    sub = cursor.fetchone()
    cursor.fetchall()

    if not sub:
        return jsonify({"error":"No submission found"}), 404

    # Verify lecturer teaches this course
    if not lec_teaches(cursor, lecturer_id, sub["course_id"]):
        return jsonify({"error":"Unauthorized"}), 403

    file_path = sub["file_path"]

    if file_path.startswith("http"):
        return jsonify({"link": file_path}), 200
    else:
        full_path = os.path.join(os.getcwd(), file_path)
        # print(f"FULL PATH: {full_path}")
        return send_file(full_path, as_attachment=True)

#Submit a grade
@assignments_bp.route("/submissions/<int:submission_id>/grade", methods=['PUT'])
def submit_grade(submission_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    data = request.get_json()
    grade = data.get("grade")

    if "user_id" not in session:
        return jsonify({"error":"Not logged in"}), 401

    user_id = session["user_id"]

    #Get lecturer
    cursor.execute(
        """ SELECT employee_id FROM Lecturer_Course_Maintainers WHERE user_id = %s """, (user_id,)
    )
    lec = cursor.fetchone()
    cursor.fetchall()

    lecturer_id = lec["employee_id"]

    #Get the submission
    cursor.execute("""
        SELECT s.student_id, a.course_id
        FROM Submission s
        JOIN Assignment a ON a.assignment_id = s.assignment_id
        WHERE s.submission_id = %s
    """, (submission_id,))
    sub_g = cursor.fetchone()
    cursor.fetchall()  # fixed

    if not sub_g:
        return jsonify({"error": "Submission not found"}), 404  # fixed

    #Verify if they should add grade
    if not lec_teaches(cursor, lecturer_id, sub_g["course_id"]):
        return jsonify({"error":"Unauthorized"}), 403

    #Add grade
    cursor.execute("""
        UPDATE Submission
        SET grade = %s
        WHERE submission_id = %s
    """, (grade, submission_id))

    db.commit()
    return jsonify({"message":"Grade successfully added"}), 200


#Compute a student's final grade
@assignments_bp.route("/<int:student_id>/finalgrade", methods=['GET'])
def get_finalgrade(student_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT AVG(grade) as avg_grade
        FROM Submission
        WHERE student_id = %s AND grade IS NOT NULL
    """, (student_id,))
    stdt_grade = cursor.fetchone()

    return jsonify({"Student's Final Grade": stdt_grade["avg_grade"]}), 200