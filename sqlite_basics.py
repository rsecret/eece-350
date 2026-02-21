import sqlite3
from typing import Iterable, Tuple


def print_table(cursor: sqlite3.Cursor, table_name: str) -> None:
    """Pretty-print the full contents of a SQLite table."""
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    print(f"\nTable: {table_name}")
    print(" | ".join(columns))
    print("-" * (len(columns) * 10))

    for row in rows:
        print(" | ".join(str(value) for value in row))


def seed_table(cursor: sqlite3.Cursor, query: str, rows: Iterable[Tuple]) -> None:
    """Bulk insert helper with simple error reporting."""
    try:
        cursor.executemany(query, rows)
    except sqlite3.IntegrityError as exc:
        raise SystemExit(f"Failed to insert seed data: {exc}") from exc


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Schema modeled after Tutorial 3, slide 24.
    cursor.execute(
        """
        CREATE TABLE student (
            student_id INTEGER PRIMARY KEY,
            name       TEXT NOT NULL,
            age        INTEGER NOT NULL CHECK(age > 0)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE registered_courses (
            student_id INTEGER NOT NULL,
            course_id  TEXT    NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE grades (
            student_id INTEGER NOT NULL,
            course_id  TEXT    NOT NULL,
            grade      REAL    NOT NULL CHECK(grade BETWEEN 0 AND 100),
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id, course_id)
                REFERENCES registered_courses(student_id, course_id)
        )
        """
    )

    students = [
        (1001, "Alice", 20),
        (1002, "Bob", 22),
        (1003, "Charlie", 21),
        (1004, "Dina", 19),
    ]
    registrations = [
        (1001, "EECE350"),
        (1001, "MATH201"),
        (1001, "STAT210"),
        (1002, "EECE350"),
        (1002, "STAT210"),
        (1003, "EECE350"),
        (1003, "PHYS210"),
        (1004, "EECE350"),
        (1004, "MATH201"),
    ]
    gradebook = [
        (1001, "EECE350", 84.5),
        (1001, "MATH201", 92.0),
        (1001, "STAT210", 88.0),
        (1002, "EECE350", 73.5),
        (1002, "STAT210", 81.0),
        (1003, "EECE350", 95.0),
        (1003, "PHYS210", 89.5),
        (1004, "EECE350", 78.0),
        (1004, "MATH201", 85.0),
    ]

    seed_table(cursor, "INSERT INTO student VALUES (?, ?, ?)", students)
    seed_table(cursor, "INSERT INTO registered_courses VALUES (?, ?)", registrations)
    seed_table(cursor, "INSERT INTO grades VALUES (?, ?, ?)", gradebook)
    conn.commit()

    for table in ("student", "registered_courses", "grades"):
        print_table(cursor, table)

    print("\nHighest grade per student (ID, name, course, grade):")
    cursor.execute(
        """
        SELECT s.student_id,
               s.name,
               g.course_id,
               g.grade
        FROM grades AS g
        JOIN (
            SELECT student_id, MAX(grade) AS max_grade
            FROM grades
            GROUP BY student_id
        ) AS mx
          ON g.student_id = mx.student_id
         AND g.grade = mx.max_grade
        JOIN student AS s
          ON s.student_id = g.student_id
        ORDER BY s.student_id, g.course_id
        """
    )
    for row in cursor.fetchall():
        print(row)

    print("\nAverage grade per student (ID, name, avg_grade):")
    cursor.execute(
        """
        SELECT s.student_id,
               s.name,
               ROUND(AVG(g.grade), 2) AS avg_grade
        FROM student AS s
        LEFT JOIN grades AS g
               ON s.student_id = g.student_id
        GROUP BY s.student_id, s.name
        ORDER BY s.student_id
        """
    )
    for row in cursor.fetchall():
        print(row)

    conn.close()


if __name__ == "__main__":
    main()
