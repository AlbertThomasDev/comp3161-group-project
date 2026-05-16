from flask import Blueprint, jsonify
from app.database import get_db

forums_bp = Blueprint('forums', __name__)

# Get all forums (courses with threads)
@forums_bp.route('/', methods=['GET'])
def get_forums():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT DISTINCT c.course_id, c.course_name
        FROM Course c
        JOIN Discussion_Thread d ON c.course_id = d.forum_id
    """)

    forums = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(forums)


# Get a single forum (course info + thread count)
@forums_bp.route('/<int:forum_id>', methods=['GET'])
def get_forum(forum_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT course_id, course_name, course_code
        FROM Course
        WHERE course_id = %s
    """, (forum_id,))
    course = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS thread_count
        FROM Discussion_Thread
        WHERE forum_id = %s AND parent_thread_id IS NULL
    """, (forum_id,))
    count = cursor.fetchone()

    cursor.close()
    db.close()

    if course:
        course['thread_count'] = count['thread_count']
        return jsonify(course)

    return jsonify({"error": "Forum not found"}), 404
