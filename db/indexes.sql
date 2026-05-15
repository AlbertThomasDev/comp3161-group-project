-- initial indexes sql file to use for optimization 
-- should help with tasks such as getting courses for student and checking if student is enrolled 

USE coursedb;

-- enrollment indexes
CREATE INDEX idx_enrolled_student
ON Enrolled_In(student_id);

CREATE INDEX idx_enrolled_course
ON Enrolled_In(course_id);

CREATE INDEX idx_enrolled_student_course
ON Enrolled_In(student_id, course_id);

-- course indexes
CREATE INDEX idx_course_lecturer
ON Course(employee_id);

-- assignment indexes
CREATE INDEX idx_assignment_course
ON Assignment(course_id);

-- submission indexes
CREATE INDEX idx_submission_student
ON Submission(student_id);

CREATE INDEX idx_submission_assignment
ON Submission(assignment_id);

-- calendar event indexes
CREATE INDEX idx_calendar_course
ON Calendar_Event(course_id);

CREATE INDEX idx_calendar_date
ON Calendar_Event(event_date);

-- thread indexes
CREATE INDEX idx_thread_forum
ON Discussion_Thread(forum_id);

CREATE INDEX idx_thread_parent
ON Discussion_Thread(parent_thread_id);
