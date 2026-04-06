USE coursedb;

-- 1. All courses that have 50 or more students
CREATE VIEW courses_with_50_or_more_students AS
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(e.student_id) AS student_count
FROM Course c
JOIN Enrolled_In e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name
HAVING COUNT(e.student_id) >= 50;

-- 2. All students that do 5 or more courses
CREATE VIEW students_with_5_or_more_courses AS
SELECT 
    s.student_id,
    u.user_name,
    COUNT(e.course_id) AS course_count
FROM Students s
JOIN Users u ON s.user_id = u.user_id
JOIN Enrolled_In e ON s.student_id = e.student_id
GROUP BY s.student_id, u.user_name
HAVING COUNT(e.course_id) >= 5;

-- 3. All lecturers that teach 3 or more courses
CREATE VIEW lecturers_with_3_or_more_courses AS
SELECT 
    l.employee_id,
    u.user_name,
    COUNT(c.course_id) AS course_count
FROM Lecturer_Course_Maintainers l
JOIN Users u ON l.user_id = u.user_id
JOIN Course c ON l.employee_id = c.employee_id
GROUP BY l.employee_id, u.user_name
HAVING COUNT(c.course_id) >= 3;

-- 4. The 10 most enrolled courses
CREATE VIEW top_10_most_enrolled_courses AS
SELECT 
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(e.student_id) AS student_count
FROM Course c
JOIN Enrolled_In e ON c.course_id = e.course_id
GROUP BY c.course_id, c.course_code, c.course_name
ORDER BY student_count DESC
LIMIT 10;

-- 5. Top 10 students with the highest overall averages
CREATE VIEW top_10_students_highest_averages AS
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