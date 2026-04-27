#route/threads.py
#file should be able to handle getting threads for a forum, creating a thread, reply to thread (nested), and getting thread with replies (possible tree)

from flask import Blueprint, request, jsonify #necessary import
from db import get_db #necessary import 

threads_bp = Blueprint('threads', __name__)

#get threads for a forum 
@threads_bp.route('/forum/<int:forum_id>', methods=['GET'])
def get_threads(forum_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT thread_id, title, content, author_id, created_at
        FROM Discussion_Thread
        WHERE forum_id = %s AND parent_thread_id IS NULL
        ORDER BY created_at DESC
    """, (forum_id,))

    threads = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(threads)

#create a thread
@threads_bp.route('/create', methods=['POST'])
def create_thread():
    data = request.get_json()

    forum_id = data.get('forum_id')
    author_id = data.get('author_id')
    title = data.get('title')
    content = data.get('content')

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO Discussion_Thread
            (forum_id, author_id, title, content, created_at, parent_thread_id)
            VALUES (%s, %s, %s, %s, NOW(), NULL)
        """, (forum_id, author_id, title, content))

        db.commit()
        return jsonify({"message": "Thread created"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        db.close()

#reply to thread
@threads_bp.route('/reply', methods=['POST'])
def reply_thread():
    data = request.get_json()

    forum_id = data.get('forum_id')
    author_id = data.get('author_id')
    content = data.get('content')
    parent_thread_id = data.get('parent_thread_id')

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO Discussion_Thread
            (forum_id, author_id, title, content, created_at, parent_thread_id)
            VALUES (%s, %s, NULL, %s, NOW(), %s)
        """, (forum_id, author_id, content, parent_thread_id))

        db.commit()
        return jsonify({"message": "Reply added"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        db.close() 

#get a thread with replies 
#tree structure
def build_thread_tree(threads, parent_id=None):
    tree = []
    for t in threads:
        if t['parent_thread_id'] == parent_id:
            children = build_thread_tree(threads, t['thread_id'])
            if children:
                t['replies'] = children
            tree.append(t)
    return tree


@threads_bp.route('/<int:thread_id>', methods=['GET'])
def get_thread_with_replies(thread_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM Discussion_Thread
        WHERE forum_id = (
            SELECT forum_id FROM Discussion_Thread WHERE thread_id = %s
        )
    """, (thread_id,))

    threads = cursor.fetchall()

    cursor.close()
    db.close()

    tree = build_thread_tree(threads)

    for t in tree:
        if t['thread_id'] == thread_id:
            return jsonify(t)

    return jsonify({"error": "Thread not found"}), 404
