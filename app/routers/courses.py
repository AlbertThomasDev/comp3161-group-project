from flask import Blueprint

courses_bp = Blueprint('courses', __name__)

# View all courses
@courses_bp.route("/courses")
def view_courses():
    print("\nViewing all courses")
    return "<h1>Courses Page</h1><p>List of all courses</p>"


# View a specific course
@courses_bp.route("/courses/<int:course_id>")
def view_course(course_id):
    print(f"\nViewing course {course_id}")
    return f"<h1>Course {course_id}</h1><p>Details for this course</p>"


# Enroll in a course
@courses_bp.route("/courses/enroll/<int:course_id>")
def enroll_course(course_id):
    print(f"\nEnrolling in course {course_id}")
    return f"<h1>Enrolled</h1><p>You have enrolled in course {course_id}</p>"


# Drop a course
@courses_bp.route("/courses/drop/<int:course_id>")
def drop_course(course_id):
    print(f"\nDropping course {course_id}")
    return f"<h1>Dropped</h1><p>You have dropped course {course_id}</p>"
