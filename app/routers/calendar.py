from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime

calendar_bp = Blueprint('calendar', __name__)


# GET all calendar events for a course
@calendar_bp.route('/course/<int:course_id>', methods=['GET'])
def get_course_events(course_id):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	cursor.execute("""
		SELECT event_id, course_id, title, event_description AS description, event_date, event_type
		FROM Calendar_Event
		WHERE course_id = %s
		ORDER BY event_date
	""", (course_id,))

	events = cursor.fetchall()
	cursor.close()
	db.close()

	return jsonify(events)


# POST create calendar event for a course
@calendar_bp.route('/course/<int:course_id>', methods=['POST'])
def create_course_event(course_id):
	data = request.get_json() or {}
	title = data.get('title')
	description = data.get('description')
	event_date = data.get('event_date')
	event_type = data.get('event_type')
	requester_id = data.get('requester_id')

	if not all([title, event_date, event_type, requester_id]):
		return jsonify({'error': 'title, event_date, event_type, requester_id required'}), 400

	# validate date
	try:
		_ = datetime.strptime(event_date, '%Y-%m-%d').date()
	except Exception:
		return jsonify({'error': 'event_date must be YYYY-MM-DD'}), 400

	# normalize event_type to DB allowed values
	allowed = ('assignment', 'lecture', 'exam')
	if event_type not in allowed:
		return jsonify({'error': f'event_type must be one of {allowed}'}), 400

	db = get_db()
	cursor = db.cursor(dictionary=True)

	# ensure course exists
	cursor.execute("SELECT course_id, employee_id FROM Course WHERE course_id = %s", (course_id,))
	course = cursor.fetchone()
	if not course:
		cursor.close()
		db.close()
		return jsonify({'error': 'Course not found'}), 404

	# check requester is admin or lecturer assigned to course
	cursor.execute("SELECT a.admin_id FROM Admins a WHERE a.user_id = %s", (requester_id,))
	admin = cursor.fetchone()
	cursor.execute("SELECT l.employee_id FROM Lecturer_Course_Maintainers l WHERE l.user_id = %s", (requester_id,))
	lecturer = cursor.fetchone()

	allowed_flag = False
	if admin and admin.get('admin_id'):
		allowed_flag = True
	if lecturer and course.get('employee_id') and lecturer.get('employee_id') == course.get('employee_id'):
		allowed_flag = True

	if not allowed_flag:
		cursor.close()
		db.close()
		return jsonify({'error': 'Unauthorized'}), 403

	try:
		cursor.execute("""
			INSERT INTO Calendar_Event (course_id, title, event_description, event_date, event_type)
			VALUES (%s, %s, %s, %s, %s)
		""", (course_id, title, description, event_date, event_type))
		db.commit()
		new_id = cursor.lastrowid
		cursor.close()
		db.close()
		return jsonify({'message': 'Event created', 'event_id': new_id}), 201
	except Exception as e:
		db.rollback()
		cursor.close()
		db.close()
		return jsonify({'error': str(e)}), 400


# GET all calendar events for all courses a student is enrolled in
@calendar_bp.route('/student/<int:student_id>', methods=['GET'])
def get_student_events(student_id):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	cursor.execute("""
		SELECT ce.event_id, ce.course_id, ce.title, ce.event_description AS description, ce.event_date, ce.event_type
		FROM Enrolled_In e
		JOIN Calendar_Event ce ON e.course_id = ce.course_id
		WHERE e.student_id = %s
		ORDER BY ce.event_date
	""", (student_id,))

	events = cursor.fetchall()
	cursor.close()
	db.close()
	return jsonify(events)


# GET events for a student on a specific date
@calendar_bp.route('/student/<int:student_id>/date/<event_date>', methods=['GET'])
def get_student_events_by_date(student_id, event_date):
	# validate date
	try:
		_ = datetime.strptime(event_date, '%Y-%m-%d').date()
	except Exception:
		return jsonify({'error': 'event_date must be YYYY-MM-DD'}), 400

	db = get_db()
	cursor = db.cursor(dictionary=True)

	cursor.execute("""
		SELECT ce.event_id, ce.course_id, ce.title, ce.event_description AS description, ce.event_date, ce.event_type
		FROM Students s
		JOIN Enrolled_In e ON s.student_id = e.student_id
		JOIN Course c ON e.course_id = c.course_id
		JOIN Calendar_Event ce ON c.course_id = ce.course_id
		WHERE s.student_id = %s AND ce.event_date = %s
		ORDER BY ce.event_date
	""", (student_id, event_date))

	events = cursor.fetchall()
	cursor.close()
	db.close()
	return jsonify(events)


# GET events on a specific date for a specific course
@calendar_bp.route('/date/<event_date>/course/<int:course_id>', methods=['GET'])
def get_course_events_by_date(event_date, course_id):
	try:
		_ = datetime.strptime(event_date, '%Y-%m-%d').date()
	except Exception:
		return jsonify({'error': 'event_date must be YYYY-MM-DD'}), 400

	db = get_db()
	cursor = db.cursor(dictionary=True)

	cursor.execute("""
		SELECT event_id, course_id, title, event_description AS description, event_date, event_type
		FROM Calendar_Event
		WHERE course_id = %s AND event_date = %s
		ORDER BY event_date
	""", (course_id, event_date))

	events = cursor.fetchall()
	cursor.close()
	db.close()
	return jsonify(events)


# PUT update a calendar event
@calendar_bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
	data = request.get_json() or {}
	title = data.get('title')
	description = data.get('description')
	event_date = data.get('event_date')
	event_type = data.get('event_type')
	requester_id = data.get('requester_id')

	if not requester_id:
		return jsonify({'error': 'requester_id required'}), 400

	if event_date:
		try:
			_ = datetime.strptime(event_date, '%Y-%m-%d').date()
		except Exception:
			return jsonify({'error': 'event_date must be YYYY-MM-DD'}), 400

	db = get_db()
	cursor = db.cursor(dictionary=True)

	# ensure event exists and get related course
	cursor.execute("SELECT event_id, course_id FROM Calendar_Event WHERE event_id = %s", (event_id,))
	event = cursor.fetchone()
	if not event:
		cursor.close()
		db.close()
		return jsonify({'error': 'Event not found'}), 404

	course_id = event.get('course_id')

	# authorization check
	cursor.execute("SELECT a.admin_id FROM Admins a WHERE a.user_id = %s", (requester_id,))
	admin = cursor.fetchone()
	cursor.execute("SELECT l.employee_id FROM Lecturer_Course_Maintainers l WHERE l.user_id = %s", (requester_id,))
	lecturer = cursor.fetchone()
	cursor.execute("SELECT employee_id FROM Course WHERE course_id = %s", (course_id,))
	course = cursor.fetchone()

	allowed_flag = False
	if admin and admin.get('admin_id'):
		allowed_flag = True
	if lecturer and course and lecturer.get('employee_id') == course.get('employee_id'):
		allowed_flag = True

	if not allowed_flag:
		cursor.close()
		db.close()
		return jsonify({'error': 'Unauthorized'}), 403

	# build update parts dynamically
	fields = []
	params = []
	if title is not None:
		if title == '':
			cursor.close()
			db.close()
			return jsonify({'error': 'title cannot be empty'}), 400
		fields.append('title = %s')
		params.append(title)
	if description is not None:
		fields.append('event_description = %s')
		params.append(description)
	if event_date is not None:
		fields.append('event_date = %s')
		params.append(event_date)
	if event_type is not None:
		allowed = ('assignment', 'lecture', 'exam')
		if event_type not in allowed:
			cursor.close()
			db.close()
			return jsonify({'error': f'event_type must be one of {allowed}'}), 400
		fields.append('event_type = %s')
		params.append(event_type)

	if not fields:
		cursor.close()
		db.close()
		return jsonify({'error': 'No fields to update'}), 400

	params.append(event_id)
	sql = f"UPDATE Calendar_Event SET {', '.join(fields)} WHERE event_id = %s"

	try:
		cursor.execute(sql, tuple(params))
		db.commit()
		cursor.close()
		db.close()
		return jsonify({'message': 'Event updated'})
	except Exception as e:
		db.rollback()
		cursor.close()
		db.close()
		return jsonify({'error': str(e)}), 400


# DELETE an event
@calendar_bp.route('/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
	data = request.get_json() or {}
	requester_id = data.get('requester_id')
	if not requester_id:
		return jsonify({'error': 'requester_id required'}), 400

	db = get_db()
	cursor = db.cursor(dictionary=True)

	cursor.execute("SELECT event_id, course_id FROM Calendar_Event WHERE event_id = %s", (event_id,))
	event = cursor.fetchone()
	if not event:
		cursor.close()
		db.close()
		return jsonify({'error': 'Event not found'}), 404

	course_id = event.get('course_id')

	#authorization check
	cursor.execute("SELECT a.admin_id FROM Admins a WHERE a.user_id = %s", (requester_id,))
	admin = cursor.fetchone()
	cursor.execute("SELECT l.employee_id FROM Lecturer_Course_Maintainers l WHERE l.user_id = %s", (requester_id,))
	lecturer = cursor.fetchone()
	cursor.execute("SELECT employee_id FROM Course WHERE course_id = %s", (course_id,))
	course = cursor.fetchone()

	allowed_flag = False
	if admin and admin.get('admin_id'):
		allowed_flag = True
	if lecturer and course and lecturer.get('employee_id') == course.get('employee_id'):
		allowed_flag = True

	if not allowed_flag:
		cursor.close()
		db.close()
		return jsonify({'error': 'Unauthorized'}), 403

	try:
		cursor.execute("DELETE FROM Calendar_Event WHERE event_id = %s", (event_id,))
		db.commit()
		cursor.close()
		db.close()
		return jsonify({'message': 'Event deleted'})
	except Exception as e:
		db.rollback()
		cursor.close()
		db.close()
		return jsonify({'error': str(e)}), 400