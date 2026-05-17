-- =====================================================
-- COMP3161 FINAL PROJECT DATABASE REQUIREMENT CHECKS
-- Presentation Evidence Script
-- =====================================================
-- Purpose:
-- Run this script during marking to show that the SQL-provable
-- database requirements have been met.
--
-- This script contains SELECT statements only.
-- It does not modify the database.
-- =====================================================


-- =====================================================
-- USER ACCOUNT AND ROLE REQUIREMENTS
-- =====================================================

SELECT 'USER ACCOUNT AND ROLE REQUIREMENTS' AS section_label;

-- Shows total registered users
SELECT COUNT(*) AS total_users FROM Users;

-- Shows total students
SELECT COUNT(*) AS total_students FROM Students;

-- Expected: total_students >= 100000
SELECT 
    COUNT(*) AS total_students,
    CASE 
        WHEN COUNT(*) >= 100000 THEN 'PASS'
        ELSE 'FAIL'
    END AS requirement_status
FROM Students;

-- Shows total lecturers
SELECT COUNT(*) AS total_lecturers FROM Lecturer_Course_Maintainers;

-- Shows total admins
SELECT COUNT(*) AS total_admins FROM Admins;

-- Shows users grouped by role
SELECT user_role, COUNT(*) AS count_per_role
FROM Users
GROUP BY user_role;

-- Shows sample student users
SELECT u.user_id, u.user_name, u.user_role, s.student_id
FROM Users u
JOIN Students s ON u.user_id = s.user_id
WHERE u.user_role = 'student'
LIMIT 10;

-- Shows sample lecturer users
SELECT u.user_id, u.user_name, u.user_role, l.employee_id
FROM Users u
JOIN Lecturer_Course_Maintainers l ON u.user_id = l.user_id
WHERE u.user_role = 'lecturer'
LIMIT 10;

-- Shows sample admin users
SELECT u.user_id, u.user_name, u.user_role, a.admin_id
FROM Users u
JOIN Admins a ON u.user_id = a.user_id
WHERE u.user_role = 'admin'
LIMIT 10;


-- =====================================================
-- COURSE CREATION AND COURSE RETRIEVAL REQUIREMENTS
-- =====================================================

SELECT 'COURSE CREATION AND COURSE RETRIEVAL REQUIREMENTS' AS section_label;

-- Shows total courses
SELECT COUNT(*) AS total_courses FROM Course;

-- Expected: total_courses >= 200
SELECT 
    COUNT(*) AS total_courses,
    CASE 
        WHEN COUNT(*) >= 200 THEN 'PASS'
        ELSE 'FAIL'
    END AS requirement_status
FROM Course;

-- Shows sample course records with core course details
SELECT 
    course_id,
    course_code,
    course_name,
    course_description,
    semester_number,
    semester_year,
    employee_id
FROM Course
ORDER BY course_id
LIMIT 20;

-- Shows courses retrieved for a sample student
SELECT DISTINCT 
    c.course_id,
    c.course_code,
    c.course_name,
    c.course_description,
    c.semester_number,
    c.semester_year
FROM Course c
JOIN Enrolled_In e ON c.course_id = e.course_id
WHERE e.student_id = (
    SELECT student_id 
    FROM Enrolled_In 
    LIMIT 1
)
ORDER BY c.course_id
LIMIT 20;

-- Shows courses retrieved for a sample lecturer
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    c.course_description,
    c.semester_number,
    c.semester_year,
    c.employee_id
FROM Course c
WHERE c.employee_id = (
    SELECT employee_id 
    FROM Course 
    WHERE employee_id IS NOT NULL 
    LIMIT 1
)
ORDER BY c.course_id
LIMIT 20;

-- Expected: zero rows returned
-- Shows courses missing a lecturer assignment
SELECT 
    course_id,
    course_code,
    course_name,
    employee_id
FROM Course
WHERE employee_id IS NULL;


-- =====================================================
-- COURSE ENROLLMENT DATA REQUIREMENTS
-- =====================================================

SELECT 'COURSE ENROLLMENT DATA REQUIREMENTS' AS section_label;

-- Shows total course enrollments
SELECT COUNT(*) AS total_enrollments FROM Enrolled_In;

-- Shows minimum, maximum, and average course load per student
SELECT 
    MIN(course_count) AS minimum_courses_per_student,
    MAX(course_count) AS maximum_courses_per_student,
    AVG(course_count) AS average_courses_per_student
FROM (
    SELECT 
        s.student_id,
        COUNT(e.course_id) AS course_count
    FROM Students s
    LEFT JOIN Enrolled_In e ON s.student_id = e.student_id
    GROUP BY s.student_id
) student_course_counts;

-- Expected: zero rows returned
-- Shows students enrolled in more than 6 courses
SELECT 
    s.student_id,
    COUNT(e.course_id) AS course_count
FROM Students s
LEFT JOIN Enrolled_In e ON s.student_id = e.student_id
GROUP BY s.student_id
HAVING COUNT(e.course_id) > 6;

-- Expected: zero rows returned
-- Shows students enrolled in fewer than 3 courses, including students with zero courses
SELECT 
    s.student_id,
    COUNT(e.course_id) AS course_count
FROM Students s
LEFT JOIN Enrolled_In e ON s.student_id = e.student_id
GROUP BY s.student_id
HAVING COUNT(e.course_id) < 3;

-- Shows minimum, maximum, and average members per course
SELECT 
    MIN(member_count) AS minimum_members_per_course,
    MAX(member_count) AS maximum_members_per_course,
    AVG(member_count) AS average_members_per_course
FROM (
    SELECT 
        c.course_id,
        COUNT(e.student_id) AS member_count
    FROM Course c
    LEFT JOIN Enrolled_In e ON c.course_id = e.course_id
    GROUP BY c.course_id
) course_member_counts;

-- Expected: zero rows returned
-- Shows courses with fewer than 10 students, including courses with zero students
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(e.student_id) AS member_count
FROM Course c
LEFT JOIN Enrolled_In e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name
HAVING COUNT(e.student_id) < 10;

-- Expected: zero rows returned
-- Shows duplicate enrollments for the same student in the same course
SELECT 
    student_id,
    course_id,
    COUNT(*) AS duplicate_count
FROM Enrolled_In
GROUP BY student_id, course_id
HAVING COUNT(*) > 1;


-- =====================================================
-- LECTURER COURSE ASSIGNMENT REQUIREMENTS
-- =====================================================

SELECT 'LECTURER COURSE ASSIGNMENT REQUIREMENTS' AS section_label;

-- Shows total courses that have assigned lecturers
SELECT COUNT(*) AS courses_with_lecturers
FROM Course
WHERE employee_id IS NOT NULL;

-- Shows lecturer course load summary
SELECT 
    MIN(course_count) AS minimum_courses_per_lecturer,
    MAX(course_count) AS maximum_courses_per_lecturer,
    AVG(course_count) AS average_courses_per_lecturer
FROM (
    SELECT 
        l.employee_id,
        COUNT(c.course_id) AS course_count
    FROM Lecturer_Course_Maintainers l
    LEFT JOIN Course c ON l.employee_id = c.employee_id
    GROUP BY l.employee_id
) lecturer_course_counts;

-- Expected: zero rows returned
-- Shows lecturers teaching more than 5 courses
SELECT 
    l.employee_id,
    u.user_name,
    COUNT(c.course_id) AS course_count
FROM Lecturer_Course_Maintainers l
LEFT JOIN Users u ON l.user_id = u.user_id
LEFT JOIN Course c ON l.employee_id = c.employee_id
GROUP BY l.employee_id, u.user_name
HAVING COUNT(c.course_id) > 5;

-- Expected: zero rows returned
-- Shows lecturers teaching fewer than 1 course
SELECT 
    l.employee_id,
    u.user_name,
    COUNT(c.course_id) AS course_count
FROM Lecturer_Course_Maintainers l
LEFT JOIN Users u ON l.user_id = u.user_id
LEFT JOIN Course c ON l.employee_id = c.employee_id
GROUP BY l.employee_id, u.user_name
HAVING COUNT(c.course_id) < 1;

-- Expected: zero rows returned
-- Since Course stores employee_id directly, this proves every course has one lecturer assigned
SELECT 
    course_id,
    course_code,
    course_name,
    employee_id
FROM Course
WHERE employee_id IS NULL;


-- =====================================================
-- COURSE MEMBERSHIP REQUIREMENTS
-- =====================================================

SELECT 'COURSE MEMBERSHIP REQUIREMENTS' AS section_label;

-- Shows members of a sample course
SELECT 
    u.user_id,
    u.user_name,
    u.user_role,
    s.student_id,
    e.course_id
FROM Users u
JOIN Students s ON u.user_id = s.user_id
JOIN Enrolled_In e ON s.student_id = e.student_id
WHERE e.course_id = (
    SELECT course_id 
    FROM Enrolled_In 
    LIMIT 1
)
ORDER BY u.user_name
LIMIT 20;

-- Shows lecturer/course maintainer for a sample course
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    l.employee_id,
    u.user_id,
    u.user_name,
    u.user_role
FROM Course c
JOIN Lecturer_Course_Maintainers l ON c.employee_id = l.employee_id
JOIN Users u ON l.user_id = u.user_id
WHERE c.course_id = (
    SELECT course_id 
    FROM Course 
    WHERE employee_id IS NOT NULL 
    LIMIT 1
);


-- =====================================================
-- CALENDAR EVENT REQUIREMENTS
-- =====================================================

SELECT 'CALENDAR EVENT REQUIREMENTS' AS section_label;

-- Shows total calendar events
SELECT COUNT(*) AS total_calendar_events FROM Calendar_Event;

-- Expected: zero rows returned
-- Shows calendar events not linked to a valid course
SELECT 
    ce.event_id,
    ce.course_id,
    ce.title,
    ce.event_date
FROM Calendar_Event ce
LEFT JOIN Course c ON ce.course_id = c.course_id
WHERE c.course_id IS NULL;

-- Shows calendar events for a sample course
SELECT 
    ce.event_id,
    ce.title,
    ce.event_date,
    ce.event_type,
    ce.course_id
FROM Calendar_Event ce
WHERE ce.course_id = (
    SELECT course_id 
    FROM Calendar_Event 
    LIMIT 1
)
ORDER BY ce.event_date
LIMIT 20;

-- Shows calendar events for a sample student through their enrolled courses
SELECT DISTINCT 
    ce.event_id,
    ce.title,
    ce.event_date,
    ce.event_type,
    ce.course_id,
    e.student_id
FROM Calendar_Event ce
JOIN Enrolled_In e ON ce.course_id = e.course_id
WHERE e.student_id = (
    SELECT student_id 
    FROM Enrolled_In 
    LIMIT 1
)
ORDER BY ce.event_date
LIMIT 20;

-- Shows calendar events for a sample student on a specific date
SELECT DISTINCT 
    ce.event_id,
    ce.title,
    ce.event_date,
    ce.event_type,
    ce.course_id,
    e.student_id
FROM Calendar_Event ce
JOIN Enrolled_In e ON ce.course_id = e.course_id
WHERE e.student_id = (
    SELECT student_id 
    FROM Enrolled_In 
    LIMIT 1
)
AND ce.event_date = (
    SELECT event_date 
    FROM Calendar_Event 
    LIMIT 1
)
ORDER BY ce.event_date
LIMIT 20;


-- =====================================================
-- FORUM AND DISCUSSION THREAD REQUIREMENTS
-- =====================================================

SELECT 'FORUM AND DISCUSSION THREAD REQUIREMENTS' AS section_label;

-- Shows total discussion forums
SELECT COUNT(*) AS total_forums FROM Discussion_Forum;

-- Expected: zero rows returned
-- Shows forums not linked to a valid course
SELECT 
    df.forum_id,
    df.title,
    df.course_id
FROM Discussion_Forum df
LEFT JOIN Course c ON df.course_id = c.course_id
WHERE c.course_id IS NULL;

-- Shows forums for a sample course
SELECT 
    df.forum_id,
    df.title,
    df.course_id
FROM Discussion_Forum df
WHERE df.course_id = (
    SELECT course_id 
    FROM Discussion_Forum 
    LIMIT 1
)
LIMIT 20;

-- Shows total discussion threads
SELECT COUNT(*) AS total_threads FROM Discussion_Thread;

-- Expected: zero rows returned
-- Shows discussion threads not linked to a valid forum
SELECT 
    dt.thread_id,
    dt.forum_id,
    dt.title,
    dt.author_id
FROM Discussion_Thread dt
LEFT JOIN Discussion_Forum df ON dt.forum_id = df.forum_id
WHERE df.forum_id IS NULL;

-- Shows threads for a sample forum
SELECT 
    dt.thread_id,
    dt.forum_id,
    dt.title,
    dt.author_id,
    dt.parent_thread_id
FROM Discussion_Thread dt
WHERE dt.forum_id = (
    SELECT forum_id 
    FROM Discussion_Thread 
    LIMIT 1
)
LIMIT 20;

-- Shows replies to discussion threads
SELECT 
    dt.thread_id,
    dt.parent_thread_id,
    dt.title,
    dt.author_id
FROM Discussion_Thread dt
WHERE dt.parent_thread_id IS NOT NULL
LIMIT 20;


-- =====================================================
-- COURSE CONTENT REQUIREMENTS
-- =====================================================

SELECT 'COURSE CONTENT REQUIREMENTS' AS section_label;

-- Shows total course sections
SELECT COUNT(*) AS total_sections FROM Section;

-- Shows total section items/content
SELECT COUNT(*) AS total_section_items FROM Section_Item;

-- Expected: zero rows returned
-- Shows sections not linked to valid courses
SELECT 
    s.section_id,
    s.course_id,
    s.title
FROM Section s
LEFT JOIN Course c ON s.course_id = c.course_id
WHERE c.course_id IS NULL;

-- Expected: zero rows returned
-- Shows section items not linked to valid sections
SELECT 
    si.item_id,
    si.section_id,
    si.title,
    si.item_type
FROM Section_Item si
LEFT JOIN Section s ON si.section_id = s.section_id
WHERE s.section_id IS NULL;

-- Shows course content separated by section
SELECT 
    si.section_id,
    si.item_id,
    si.title,
    si.item_type,
    si.item_order
FROM Section_Item si
ORDER BY si.section_id, si.item_order
LIMIT 20;

-- Shows different course content item types
SELECT 
    item_type,
    COUNT(*) AS count_per_type
FROM Section_Item
GROUP BY item_type;

-- Shows all course content for a sample course
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    s.section_id,
    s.title AS section_title,
    si.item_id,
    si.title AS item_title,
    si.item_type,
    si.file_path,
    si.section_url,
    si.item_order
FROM Course c
JOIN Section s ON c.course_id = s.course_id
JOIN Section_Item si ON s.section_id = si.section_id
WHERE c.course_id = (
    SELECT course_id 
    FROM Section 
    LIMIT 1
)
ORDER BY s.section_id, si.item_order
LIMIT 50;


-- =====================================================
-- ASSIGNMENT AND SUBMISSION REQUIREMENTS
-- =====================================================

SELECT 'ASSIGNMENT AND SUBMISSION REQUIREMENTS' AS section_label;

-- Shows total assignments
SELECT COUNT(*) AS total_assignments FROM Assignment;

-- Shows total submissions
SELECT COUNT(*) AS total_submissions FROM Submission;

-- Expected: zero rows returned
-- Shows assignments not linked to valid courses
SELECT 
    a.assignment_id,
    a.course_id,
    a.title
FROM Assignment a
LEFT JOIN Course c ON a.course_id = c.course_id
WHERE c.course_id IS NULL;

-- Expected: zero rows returned
-- Shows submissions not linked to valid assignments
SELECT 
    sub.submission_id,
    sub.assignment_id,
    sub.student_id
FROM Submission sub
LEFT JOIN Assignment a ON sub.assignment_id = a.assignment_id
WHERE a.assignment_id IS NULL;

-- Expected: zero rows returned
-- Shows submissions not linked to valid students
SELECT 
    sub.submission_id,
    sub.assignment_id,
    sub.student_id
FROM Submission sub
LEFT JOIN Students s ON sub.student_id = s.student_id
WHERE s.student_id IS NULL;

-- Shows sample submissions with grades and feedback
SELECT 
    submission_id,
    assignment_id,
    student_id,
    submission_date,
    file_path,
    feedback,
    grade
FROM Submission
LIMIT 20;

-- Shows total graded submissions
SELECT COUNT(*) AS graded_submissions
FROM Submission
WHERE grade IS NOT NULL;

-- Shows calculated student averages from grades
SELECT 
    s.student_id,
    u.user_name,
    AVG(sub.grade) AS average_grade
FROM Students s
JOIN Users u ON s.user_id = u.user_id
JOIN Submission sub ON s.student_id = sub.student_id
WHERE sub.grade IS NOT NULL
GROUP BY s.student_id, u.user_name
ORDER BY average_grade DESC
LIMIT 20;


-- =====================================================
-- REQUIRED REPORTS AND VIEWS
-- =====================================================

SELECT 'REQUIRED REPORTS AND VIEWS' AS section_label;

-- Report: all courses that have 50 or more students
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(e.student_id) AS student_count
FROM Course c
JOIN Enrolled_In e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name
HAVING COUNT(e.student_id) >= 50
ORDER BY student_count DESC;

-- Report: all students that do 5 or more courses
SELECT 
    s.student_id,
    u.user_name,
    COUNT(e.course_id) AS course_count
FROM Students s
JOIN Users u ON s.user_id = u.user_id
JOIN Enrolled_In e ON s.student_id = e.student_id
GROUP BY s.student_id, u.user_name
HAVING COUNT(e.course_id) >= 5
ORDER BY course_count DESC;

-- Report: all lecturers that teach 3 or more courses
SELECT 
    l.employee_id,
    u.user_name,
    COUNT(c.course_id) AS course_count
FROM Lecturer_Course_Maintainers l
JOIN Users u ON l.user_id = u.user_id
JOIN Course c ON l.employee_id = c.employee_id
GROUP BY l.employee_id, u.user_name
HAVING COUNT(c.course_id) >= 3
ORDER BY course_count DESC;

-- Report: the 10 most enrolled courses
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(e.student_id) AS enrollment_count
FROM Course c
JOIN Enrolled_In e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name
ORDER BY enrollment_count DESC
LIMIT 10;

-- Report: the top 10 students with the highest overall averages
SELECT 
    s.student_id,
    u.user_name,
    AVG(sub.grade) AS overall_average
FROM Students s
JOIN Users u ON s.user_id = u.user_id
JOIN Submission sub ON s.student_id = sub.student_id
WHERE sub.grade IS NOT NULL
GROUP BY s.student_id, u.user_name
ORDER BY overall_average DESC
LIMIT 10;


-- =====================================================
-- FINAL DATA VOLUME AND RULE VALIDATION SUMMARY
-- =====================================================

SELECT 'FINAL DATA VOLUME AND RULE VALIDATION SUMMARY' AS section_label;

-- Requirement: at least 100,000 students
SELECT 
    'At least 100,000 students' AS requirement_checked,
    COUNT(*) AS actual_value,
    '100000 or more' AS expected_value,
    CASE 
        WHEN COUNT(*) >= 100000 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM Students;

-- Requirement: at least 200 courses
SELECT 
    'At least 200 courses' AS requirement_checked,
    COUNT(*) AS actual_value,
    '200 or more' AS expected_value,
    CASE 
        WHEN COUNT(*) >= 200 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM Course;

-- Requirement: no student can do more than 6 courses
SELECT 
    'No student can do more than 6 courses' AS requirement_checked,
    COUNT(*) AS violation_count,
    '0 violations' AS expected_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT 
        s.student_id,
        COUNT(e.course_id) AS course_count
    FROM Students s
    LEFT JOIN Enrolled_In e ON s.student_id = e.student_id
    GROUP BY s.student_id
    HAVING COUNT(e.course_id) > 6
) violations;

-- Requirement: every student must be enrolled in at least 3 courses
SELECT 
    'Every student must be enrolled in at least 3 courses' AS requirement_checked,
    COUNT(*) AS violation_count,
    '0 violations' AS expected_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT 
        s.student_id,
        COUNT(e.course_id) AS course_count
    FROM Students s
    LEFT JOIN Enrolled_In e ON s.student_id = e.student_id
    GROUP BY s.student_id
    HAVING COUNT(e.course_id) < 3
) violations;

-- Requirement: each course must have at least 10 members
SELECT 
    'Each course must have at least 10 members' AS requirement_checked,
    COUNT(*) AS violation_count,
    '0 violations' AS expected_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT 
        c.course_id,
        COUNT(e.student_id) AS member_count
    FROM Course c
    LEFT JOIN Enrolled_In e ON c.course_id = e.course_id
    GROUP BY c.course_id
    HAVING COUNT(e.student_id) < 10
) violations;

-- Requirement: no lecturer can teach more than 5 courses
SELECT 
    'No lecturer can teach more than 5 courses' AS requirement_checked,
    COUNT(*) AS violation_count,
    '0 violations' AS expected_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT 
        l.employee_id,
        COUNT(c.course_id) AS course_count
    FROM Lecturer_Course_Maintainers l
    LEFT JOIN Course c ON l.employee_id = c.employee_id
    GROUP BY l.employee_id
    HAVING COUNT(c.course_id) > 5
) violations;

-- Requirement: every lecturer must teach at least 1 course
SELECT 
    'Every lecturer must teach at least 1 course' AS requirement_checked,
    COUNT(*) AS violation_count,
    '0 violations' AS expected_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT 
        l.employee_id,
        COUNT(c.course_id) AS course_count
    FROM Lecturer_Course_Maintainers l
    LEFT JOIN Course c ON l.employee_id = c.employee_id
    GROUP BY l.employee_id
    HAVING COUNT(c.course_id) < 1
) violations;

-- Requirement: every course must have a lecturer assigned
SELECT 
    'Every course must have a lecturer assigned' AS requirement_checked,
    COUNT(*) AS violation_count,
    '0 violations' AS expected_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM Course
WHERE employee_id IS NULL;

-- Requirement: no duplicate student-course enrollments
SELECT 
    'No duplicate student-course enrollments' AS requirement_checked,
    COUNT(*) AS violation_count,
    '0 violations' AS expected_value,
    CASE 
        WHEN COUNT(*) = 0 THEN 'PASS'
        ELSE 'FAIL'
    END AS status
FROM (
    SELECT 
        student_id,
        course_id,
        COUNT(*) AS duplicate_count
    FROM Enrolled_In
    GROUP BY student_id, course_id
    HAVING COUNT(*) > 1
) violations;


-- =====================================================
-- END OF DATABASE REQUIREMENT CHECK SCRIPT
-- =====================================================

SELECT 'END OF DATABASE REQUIREMENT CHECK SCRIPT' AS section_label;