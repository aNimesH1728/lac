from db import get_connection, init_db
from auth import hash_password

COURSES = ["DBMS", "OS", "DSA", "CN", "OOP", "COA", "FCS"]

STUDENTS = [
    {
        "student_id": "S001",
        "name": "Animesh Sahoo",
        "roll_number": "123CS0216",
        "password": "testpass123",
        "branch": "CSE",
        "semester": 6,
    }
]


def seed():
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    for s in STUDENTS:
        cur.execute("""
            INSERT OR IGNORE INTO students (student_id, name, roll_number, password_hash, branch, semester)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            s["student_id"], s["name"], s["roll_number"],
            hash_password(s["password"]), s["branch"], s["semester"],
        ))

        import random
        random.seed(hash(s["student_id"]))  

        for course in COURSES:
            attendance_pct = round(random.uniform(60, 98), 1)
            cur.execute("""
                INSERT INTO attendance (student_id, course_code, percentage)
                VALUES (?, ?, ?)
            """, (s["student_id"], course, attendance_pct))

            marks_scored = round(random.uniform(15, 30), 1)
            cur.execute("""
                INSERT INTO marks (student_id, course_code, exam_type, marks, max_marks)
                VALUES (?, ?, ?, ?, ?)
            """, (s["student_id"], course, "mid_semester", marks_scored, 30))

    conn.commit()
    conn.close()
    print(f"Seeded {len(STUDENTS)} students with attendance and marks across {len(COURSES)} courses")


if __name__ == "__main__":
    seed()