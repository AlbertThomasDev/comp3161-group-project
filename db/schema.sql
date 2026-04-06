CREATE DATABASE IF NOT EXISTS coursedb;
USE coursedb;

-- Users and Specializations
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL UNIQUE,
    user_password VARCHAR(255) NOT NULL,
    user_role ENUM('student', 'admin', 'lecturer') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    major VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
) AUTO_INCREMENT = 111000001;

CREATE TABLE Admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    access_level VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
) AUTO_INCREMENT = 333000001;

CREATE TABLE Lecturer_Course_Maintainers (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    department VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
) AUTO_INCREMENT = 222000001;

-- Course
CREATE TABLE Course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL,
    course_description TEXT,
    semester_number TINYINT NOT NULL,
    semester_year YEAR NOT NULL,
    employee_id INT,
    created_by INT,
    FOREIGN KEY (employee_id) REFERENCES Lecturer_Course_Maintainers(employee_id),
    FOREIGN KEY (created_by) REFERENCES Admins(admin_id)
);

CREATE TABLE Enrolled_In (
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    date_enrolled DATE,
    enroll_status ENUM('enrolled', 'completed', 'dropped') DEFAULT 'enrolled',
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

-- Forums and Threads
CREATE TABLE Discussion_Forum (
    forum_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

CREATE TABLE Discussion_Thread (
    thread_id INT AUTO_INCREMENT PRIMARY KEY,
    forum_id INT NOT NULL,
    author_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    parent_thread_id INT DEFAULT NULL,
    FOREIGN KEY (forum_id) REFERENCES Discussion_Forum(forum_id),
    FOREIGN KEY (author_id) REFERENCES Users(user_id),
    FOREIGN KEY (parent_thread_id) REFERENCES Discussion_Thread(thread_id)
);

-- Assignments and Submissions
CREATE TABLE Assignment (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    assignment_description TEXT,
    due_date DATE,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

CREATE TABLE Submission (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255),
    grade DECIMAL(5,2),
    feedback TEXT,
    FOREIGN KEY (assignment_id) REFERENCES Assignment(assignment_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id)
);

-- Course Content
CREATE TABLE Section (
    section_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

CREATE TABLE Section_Item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    item_type ENUM('link', 'file', 'assignment', 'slides') NOT NULL,
    file_path VARCHAR(255),
    section_url VARCHAR(255),
    item_order INT,
    assignment_id INT DEFAULT NULL,
    FOREIGN KEY (section_id) REFERENCES Section(section_id),
    FOREIGN KEY (assignment_id) REFERENCES Assignment(assignment_id)
);

-- Calendar
CREATE TABLE Calendar_Event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    event_description TEXT,
    event_date DATE NOT NULL,
    event_type ENUM('assignment', 'lecture', 'exam') NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);