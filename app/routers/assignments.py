from flask import Blueprint

assignments_bp = Blueprint('assignments', __name__)

# View all assignments
@assignments_bp.route("/assignments")
def view_assignments():
    print("\nViewing all assignments")
    return "<h1>Assignments Page</h1><p>List of all assignments</p>"


# View assignments for a course
@assignments_bp.route("/assignments/<int:course_id>")
def view_course_assignments(course_id):
    print(f"\nViewing assignments for course {course_id}")
    return f"<h1>Assignments</h1><p>Assignments for course {course_id}</p>"


# View a specific assignment
@assignments_bp.route("/assignments/view/<int:assignment_id>")
def view_assignment(assignment_id):
    print(f"\nViewing assignment {assignment_id}")
    return f"<h1>Assignment {assignment_id}</h1><p>Assignment details here</p>"


# Submit an assignment
@assignments_bp.route("/assignments/submit/<int:assignment_id>")
def submit_assignment(assignment_id):
    print(f"\nSubmitting assignment {assignment_id}")
    return f"<h1>Submitted</h1><p>Assignment {assignment_id} submitted successfully</p>"


# View submission status
@assignments_bp.route("/assignments/status/<int:assignment_id>")
def submission_status(assignment_id):
    print(f"\nChecking submission status for assignment {assignment_id}")
    return f"<h1>Status</h1><p>Status for assignment {assignment_id}</p>"
