#python file to generate SQL inserts 
#uses batch inserts for performance 
#constraints: 100,000 students, 200 courses, 3-6 courses for each student,
#each course must have at least 10 students (≥ 10 students), 1-5 courses for each lecturer

from faker import Faker #necessary import to create realistic-looking data
import random #necessary import 

fake = Faker()

MAJORS = [
    "Computer Science", "Information Technology", "Software Engineering",
    "Electrical Engineering", "Mechanical Engineering", "Civil Engineering",
    "Business Administration", "Accounting", "Economics", "Mathematics",
    "Physics", "Biology", "Chemistry", "Psychology", "Law"
]

DEPARTMENTS = [
    "Computer Science", "Mathematics", "Physics", "Engineering",
    "Business", "Biology", "Chemistry", "Law", "Economics"
]

#configuration
NUM_STUDENTS = 100_000 #constraint
NUM_COURSES = 200 #constraint 
NUM_ADMINS = 10 
NUM_LECTURERS = 100 #enough to distribute courses

BATCH_SIZE = 1000 #performance control

#output files
user_file = open("users.sql", "w", encoding="utf-8")
course_file = open("courses.sql", "w", encoding="utf-8")
enrollment_file = open("enrollments.sql", "w", encoding="utf-8")
extra_file = open("extras.sql", "w", encoding="utf-8")

#batch insert helper
def batch_insert(file, table, columns, values):
    """
    Writes batch insert SQL:
    INSERT INTO table (col1, col2) VALUES (...), (...), (...);
    """
    if not values:
        return
    
    cols = ", ".join(columns)
    vals = ",\n".join(values)
    
    file.write(f"INSERT INTO {table} ({cols}) VALUES\n{vals};\n\n")

#1.generate users & roles 
print("-- USERS", file=user_file)

user_id = 1  # Users table starts at 1
student_id = 111000001  # Students table starts here
lecturer_id = 222000001  # Lecturer_Course_Maintainers starts here
admin_id = 333000001  # Admins table starts here

student_ids = []
lecturer_ids = []
admin_ids = []
user_ids = []  # track all user_ids for forum/thread author reference

user_values = []
student_values = []
lecturer_values = []
admin_values = []

#generate students
for i in range(NUM_STUDENTS):
    name = fake.name().replace("'", "''")
    email = f"student{i}@school.com"

    user_values.append(
        f"({user_id}, '{name}', '{email}', 'pass', 'student', NOW())"
    )
    student_values.append(
        f"({student_id}, {user_id}, '{random.choice(MAJORS)}')"
    )

    student_ids.append(student_id)
    user_ids.append(user_id)
    user_id += 1
    student_id += 1

    #flush batch - delay buffering
    if len(user_values) >= BATCH_SIZE:
        batch_insert(user_file, "Users",
            ["user_id","user_name","user_email","user_password","user_role","created_at"],
            user_values)
        user_values = []

        batch_insert(user_file, "Students",
            ["student_id","user_id","major"],
            student_values)
        student_values = []

#generate lecturers
for i in range(NUM_LECTURERS):
    name = fake.name().replace("'", "''")

    user_values.append(
        f"({user_id}, '{name}', 'lecturer{i}@school.com', 'pass', 'lecturer', NOW())"
    )
    lecturer_values.append(
        f"({lecturer_id}, {user_id}, '{random.choice(DEPARTMENTS)}')"
    )

    lecturer_ids.append(lecturer_id)
    user_ids.append(user_id)
    user_id += 1
    lecturer_id += 1

#generate admins 
for i in range(NUM_ADMINS):
    name = fake.name().replace("'", "''")

    user_values.append(
        f"({user_id}, '{name}', 'admin{i}@school.com', 'pass', 'admin', NOW())"
    )
    admin_values.append(
        f"({admin_id}, {user_id}, 'high')"
    )

    admin_ids.append(admin_id)
    user_ids.append(user_id)
    user_id += 1
    admin_id += 1

#flush remaining
batch_insert(user_file, "Users",
    ["user_id","user_name","user_email","user_password","user_role","created_at"],
    user_values)

batch_insert(user_file, "Students",
    ["student_id","user_id","major"],
    student_values)

batch_insert(user_file, "Lecturer_Course_Maintainers",
    ["employee_id","user_id","department"],
    lecturer_values)

batch_insert(user_file, "Admins",
    ["admin_id","user_id","access_level"],
    admin_values)

#2.generate courses
print("-- COURSES", file=course_file)
course_values = []
course_ids = []

#each lecturer teaches 1–5 courses
lecturer_course_count = {lid: 0 for lid in lecturer_ids}

for cid in range(1, NUM_COURSES + 1):
    while True:
        lecturer = random.choice(lecturer_ids)
        if lecturer_course_count[lecturer] < 5:
            lecturer_course_count[lecturer] += 1
            break

    admin = random.choice(admin_ids)

    course_values.append(
        f"({cid}, 'CSE{cid:03}', 'Course {cid}', 'Desc', 1, 2025, {lecturer}, {admin})"
    )

    course_ids.append(cid)

    if len(course_values) >= BATCH_SIZE:
        batch_insert(course_file, "Course",
            ["course_id","course_code","course_name","course_description",
             "semester_number","semester_year","employee_id","created_by"],
            course_values)
        course_values = []

batch_insert(course_file, "Course",
    ["course_id","course_code","course_name","course_description",
     "semester_number","semester_year","employee_id","created_by"],
    course_values)

#every lecturer has at least 1 course
for lecturer, count in lecturer_course_count.items():
    if count == 0:
        cid = random.choice(course_ids)
        print(f"UPDATE Course SET employee_id = {lecturer} WHERE course_id = {cid};", file=course_file)

#3.generate enrollments
#attempt method to remove possible duplicates 
print("-- ENROLLMENTS", file=enrollment_file)

enroll_values = []
enrolled_set = set()  #track (student_id, course_id)

#ensure each course has at least 10 students
for cid in course_ids:
    selected_students = random.sample(student_ids, 10)

    for sid in selected_students:
        if (sid, cid) not in enrolled_set:
            enroll_values.append(
                f"({sid}, {cid}, CURDATE(), 'enrolled')"
            )
            enrolled_set.add((sid, cid))

#assign each student 3–6 courses
for sid in student_ids:
    num_courses = random.randint(3, 6)
    chosen_courses = random.sample(course_ids, num_courses)

    for cid in chosen_courses:
       if (sid, cid) not in enrolled_set:
            enroll_values.append(
                f"({sid}, {cid}, CURDATE(), 'enrolled')"
            )
            enrolled_set.add((sid, cid))

    #batch flush
    if len(enroll_values) >= BATCH_SIZE:
        batch_insert(enrollment_file, "Enrolled_In",
            ["student_id","course_id","date_enrolled","enroll_status"],
            enroll_values)
        enroll_values = []

#flush remaining
batch_insert(enrollment_file, "Enrolled_In",
    ["student_id","course_id","date_enrolled","enroll_status"],
    enroll_values)

#4.forums/threads
forum_vals = []
thread_vals = []

forum_id = 1
thread_id = 1

for cid in course_ids:
    forum_vals.append(
        f"({forum_id}, {cid}, 'Forum {cid}')"
    )

    for _ in range(5):  #5 threads per course
        user = random.choice(user_ids)  # fixed: uses user_ids not student_ids
        thread_vals.append(
            f"({thread_id}, {forum_id}, {user}, 'Title', 'Content', NOW(), NULL)"
        )
        thread_id += 1

    forum_id += 1

batch_insert(extra_file, "Discussion_Forum",
    ["forum_id","course_id","title"], forum_vals)

batch_insert(extra_file, "Discussion_Thread",
    ["thread_id","forum_id","author_id","title","content","created_at","parent_thread_id"],
    thread_vals)

#5.assignments&submissions
assignment_vals = []
submission_vals = []

assignment_id = 1
submission_id = 1

for cid in course_ids:
    for _ in range(3):  #3 assignments per course
        assignment_vals.append(
            f"({assignment_id}, {cid}, 'Assignment', 'Desc', CURDATE())"
        )

        for sid in random.sample(student_ids, 20):
            submission_vals.append(
                f"({submission_id}, {assignment_id}, {sid}, NOW(), 'file.pdf', {random.randint(50,100)}, 'Good')"
            )
            submission_id += 1

        assignment_id += 1

batch_insert(extra_file, "Assignment",
    ["assignment_id","course_id","title","assignment_description","due_date"],
    assignment_vals)

batch_insert(extra_file, "Submission",
    ["submission_id","assignment_id","student_id","submission_date","file_path","grade","feedback"],
    submission_vals)

#6.sections + section items
section_vals = []
section_item_vals = []

section_id = 1
item_id = 1

SECTION_NAMES = [
    "Introduction",
    "Lecture Notes",
    "Assignments",
    "Labs",
    "Resources"
]

ITEM_TYPES = ["link", "file", "slides"]

for cid in course_ids:

    # 2-4 sections per course
    num_sections = random.randint(2, 4)

    for _ in range(num_sections):

        section_title = random.choice(SECTION_NAMES)

        section_vals.append(
            f"({section_id}, {cid}, '{section_title}')"
        )

        # 3-5 items per section
        num_items = random.randint(3, 5)

        for order in range(1, num_items + 1):

            item_type = random.choice(ITEM_TYPES)

            title = fake.sentence(nb_words=3).replace("'", "''")

            if item_type == "link":
                file_path = "NULL"
                section_url = f"'https://example.com/resource/{item_id}'"

            else:
                file_path = f"'/files/resource_{item_id}.pdf'"
                section_url = "NULL"

            section_item_vals.append(
                f"""(
                    {item_id},
                    {section_id},
                    '{title}',
                    '{item_type}',
                    {file_path},
                    {section_url},
                    {order},
                    NULL
                )"""
            )

            item_id += 1

        section_id += 1

batch_insert(extra_file, "Section",
    ["section_id","course_id","title"],
    section_vals)

batch_insert(extra_file, "Section_Item",
    ["item_id","section_id","title","item_type",
     "file_path","section_url","item_order","assignment_id"],
    section_item_vals)


#7.calendar events
calendar_vals = []

event_id = 1

EVENT_TYPES = ["assignment", "lecture", "exam"]

for cid in course_ids:

    # 2-3 events per course
    num_events = random.randint(2, 3)

    for _ in range(num_events):

        title = fake.sentence(nb_words=4).replace("'", "''")
        description = fake.text(max_nb_chars=100).replace("'", "''")

        month = random.randint(1, 12)
        day = random.randint(1, 28)

        event_date = f"2025-{month:02}-{day:02}"

        event_type = random.choice(EVENT_TYPES)

        calendar_vals.append(
            f"""(
                {event_id},
                {cid},
                '{title}',
                '{description}',
                '{event_date}',
                '{event_type}'
            )"""
        )

        event_id += 1

batch_insert(extra_file, "Calendar_Event",
    ["event_id","course_id","title",
     "event_description","event_date","event_type"],
    calendar_vals)


#close files
user_file.close()
course_file.close()
enrollment_file.close()
extra_file.close()

print("DONE generating optimized SQL files") #print statement
