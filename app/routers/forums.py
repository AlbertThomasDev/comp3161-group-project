from flask import Blueprint

forums_bp = Blueprint('forums', __name__)

# View all forums
@forums_bp.route("/forums")
def view_forums():
    print("\nViewing all forums")
    return "<h1>Forums Page</h1><p>All discussion forums</p>"


# View threads for a course
@forums_bp.route("/forums/<int:course_id>")
def view_threads(course_id):
    print(f"\nViewing threads for course {course_id}")
    return f"<h1>Threads</h1><p>Threads for course {course_id}</p>"


# View a single thread
@forums_bp.route("/forums/thread/<int:thread_id>")
def view_thread(thread_id):
    print(f"\nViewing thread {thread_id}")
    return f"<h1>Thread {thread_id}</h1><p>Thread content here</p>"


# Create a new thread
@forums_bp.route("/forums/create")
def create_thread():
    print("\nCreating a new thread")
    return "<h1>Create Thread</h1><p>Thread created successfully</p>"


# Reply to a thread
@forums_bp.route("/forums/reply/<int:thread_id>")
def reply_thread(thread_id):
    print(f"\nReplying to thread {thread_id}")
    return f"<h1>Reply</h1><p>Reply added to thread {thread_id}</p>"
