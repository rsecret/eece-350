import sqlite3

# Connect to SQLite (in memory for testing)
conn = sqlite3.connect(':memory:')

# this is important because foreign keys are OFF by default in SQLite
conn.execute("PRAGMA foreign_keys = ON;")

cursor = conn.cursor()

# Helper function to inspect table contents
def print_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    print(f"\nTable: {table_name}")
    print(" | ".join(columns))
    print("-" * 30)

    for row in rows:
        print(" | ".join(str(value) for value in row))

# Create tables
cursor.execute("""
CREATE TABLE student (
    student_id INT PRIMARY KEY,
    name TEXT NOT NULL,
    age INT
)
""")

cursor.execute("""
CREATE TABLE registered_courses (
    student_id INT NOT NULL,
    course_id TEXT NOT NULL,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE grades (
    student_id INT NOT NULL,
    course_id TEXT NOT NULL,
    grade REAL NOT NULL,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id, course_id)
        REFERENCES registered_courses(student_id, course_id)
        ON DELETE CASCADE
)
""")
students = [
    (1, 'Alice', 20),
    (2, 'Bob', 22),
    (3, 'Charlie', 21)
]
cursor.executemany("INSERT INTO student VALUES (?, ?, ?)", students)
registered = [
    (1, 'STAT 230'),
    (1, 'EECE 350'),
    (2, 'STAT 230'),
    (3, 'EECE 350')
]
cursor.executemany("INSERT INTO registered_courses VALUES (?, ?)", registered)
grades = [
    (1, 'STAT 230', 58),
    (1, 'EECE 350', 61),
    (2, 'STAT 230', 49),
    (3, 'EECE 350', 55)
]
cursor.executemany("INSERT INTO grades VALUES (?, ?, ?)", grades)
conn.commit()
print_table(cursor, "student")
print_table(cursor, "registered_courses")
print_table(cursor, "grades")
cursor.execute("""
SELECT g.student_id, s.name, g.course_id, g.grade AS max_grade
FROM grades g
JOIN student s ON s.student_id = g.student_id
JOIN (
    SELECT student_id, MAX(grade) AS max_grade
    FROM grades
    GROUP BY student_id
) m ON m.student_id = g.student_id AND m.max_grade = g.grade
ORDER BY g.student_id, g.course_id
""")
print("\nResult of: Max grade per student (with course)")
for row in cursor.fetchall():
    print(row)
cursor.execute("""
SELECT g.student_id, s.name, ROUND(AVG(g.grade), 2) AS avg_grade
FROM grades g
JOIN student s ON s.student_id = g.student_id
GROUP BY g.student_id
ORDER BY g.student_id
""")
print("\nResult of: Average grade per student")
for row in cursor.fetchall():
    print(row)

conn.close()