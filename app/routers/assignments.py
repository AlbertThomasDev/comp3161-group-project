from flask import Blueprint, request, jsonify, session, send_file
from app.database import get_db

assignments_bp = Blueprint('assignments', __name__)

#Submit an assignment
@assignments_bp.route("/submit_assignment", methods=['POST'])
def submit_assignment():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if "user_id" not in session:
        return jsonify({"error":"Not logged in"}), 401

    user_id = session["user_id"]

    #Get student
    cursor.execute(
        """ SELECT student_id FROM Students WHERE user_id = %s """, (user_id,)
    )
    sdt = cursor.fetchone()

    student_id = sdt["student_id"]

    #Get the assigment details whether link or file
    course_name = request.form.get("course_name")
    assignment_name = request.form.get("assignment_name")
    link = request.form.get("link")
    file = request.files.get("file")

    if not course_name or not assignment_name:
        return jsonify({"error":"Course or Assignment name are required"}), 400
    
    #Find course_id to link student and assignment
    cursor.execute("""
        SELECT course_id FROM Course WHERE course_name = %s
    """, (course_name,))
    course = cursor.fetchone()
    if not course:
        return jsonify({"error":"Course not found"}), 400
    
    course_id = course["course_id"]

    #Checking if student is enrolled in course
    cursor.execute("""
    SELECT * FROM Enrolled_In WHERE student_id = %s AND course_id = %s""",
        (student_id,course_id))

    if not cursor.fetchone():
        return jsonify({"error":"You're not enrolled in this course"}), 403

    #Find assignment
    cursor.execute("""
        SELECT assignment_id FROM Assignment WHERE course_id = %s AND title = %s
    """, (course_id,assignment_name))
    
    assignment = cursor.fetchone()
    if not assignment:
        return jsonify({"error":"Assigment not found"}), 404
    
    assignment_id = assignment["assignment_id"]

    #Check if submission was already made
    cursor.execute("""
        SELECT submission_id
        FROM Submission
        WHERE student_id = %s AND assignment_id = %s
    """, (student_id,assignment_id))
    exist = cursor.fetchone()

    #Handling the file or link for submission
    if file:
        filename = file.filename
        filedir = f"uploads/{filename}"
        file.save(filedir)
        file_path = filedir
    elif link:
        file_path = link
    else:
        return jsonify({"error":"No file or link submitted"}), 400

    if exist:
        cursor.execute("""
            UPDATE Submission
            SET file_path = %s, submission_date = NOW()
            WHERE submission_id = %s
        """,(file_path,exist["submission_id"]))
    else:    
    #Submit assignment
        cursor.execute("""
            INSERT INTO Submission (assignment_id, student_id, submission_date, file_path) 
            VALUES (%s,%s,NOW(),%s)""", (assignment_id, student_id,file_path))

    db.commit()
    return jsonify({"message":"Assignment submitted"}), 201

#If Lecturer teaches a course
def lec_teaches(cursor,lecturer_id,course_id):
    cursor.execute("""
        SELECT * FROM Course 
        WHERE employee_id = %s AND course_id = %s""", (lecturer_id,course_id))
    return cursor.fetchone() is not None

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

    lecturer_id = lec["employee_id"]

    #Get the course for the assignment
    cursor.execute("""
            SELECT assignment_id, course_id FROM Assignment WHERE title = %s
    """, (title,))
    assignment = cursor.fetchone()

    if not assignment:
        return jsonify({"error":"Assignment not found"}),404

    course_id = assignment["course_id"]
    assignment_id = assignment["assignment_id"]

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
@assignments_bp.route("/submissions/<int:student_id>/download", methods=['GET'])
def download_assignments(student_id):
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

    #retrieve assignment from student
    cursor.execute("""
        SELECT s.file_path, a.course_id
        FROM Submission s
        JOIN Assignment a ON a.assignment_id = s.assignment_id
        WHERE s.student_id = %s
    """, (student_id,))
    sub = cursor.fetchone()
    cursor.fetchall()

    if not sub:
        return jsonify({"error":"Student has no submissions for this assignment."})

    #Verify if they should download assignment
    if not lec_teaches(cursor,lecturer_id,sub["course_id"]):
        return jsonify({"error":"Unauthorized"}), 403
    
    #download the submission
    ASSIGNMENT_FD = os.getcwd()
    fd_path = os.path.join(ASSIGNMENT_FD, sub["file_path"])

    if not os.path.exists(fd_path):
        return jsonify({"error": "File not found"})
    return send_file(fd_path, as_attachment=True,download_name=os.path.basename(fd_path))

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

    if not sub_g:
        return jsonify({"error": "Submission not found"})

    #Verify if they should add grade
    if not lec_teaches(cursor,lecturer_id,sub_g["course_id"]):
        return jsonify({"error":"Unauthorized"}), 403

    #Add grade
    cursor.execute("""
        UPDATE Submission
        SET grade = %s
        WHERE submission_id = %s
    """, (grade, submission_id))

    db.commit()
    return jsonify({"message":"Grade successfully added"}), 200

