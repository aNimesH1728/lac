from db import get_connection


def get_attendance(student_id: str, course_code: str | None = None):
    conn = get_connection()
    cur = conn.cursor()
    if course_code:
        cur.execute(
            "SELECT course_code, percentage FROM attendance WHERE student_id = ? AND course_code = ?",
            (student_id, course_code),
        )
    else:
        cur.execute(
            "SELECT course_code, percentage FROM attendance WHERE student_id = ?",
            (student_id,),
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_marks(student_id: str, course_code: str | None = None):
    conn = get_connection()
    cur = conn.cursor()
    if course_code:
        cur.execute(
            "SELECT course_code, exam_type, marks, max_marks FROM marks WHERE student_id = ? AND course_code = ?",
            (student_id, course_code),
        )
    else:
        cur.execute(
            "SELECT course_code, exam_type, marks, max_marks FROM marks WHERE student_id = ?",
            (student_id,),
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def file_complaint(student_id: str, category: str, description: str) -> int | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO complaints (student_id, category, description) VALUES (?, ?, ?)",
        (student_id, category, description),
    )
    conn.commit()
    complaint_id = cur.lastrowid
    conn.close()
    return complaint_id


if __name__ == "__main__":
    # Manual test — run after seed.py
    print("All attendance for S001:", get_attendance("S001"))
    print("\nDBMS attendance for S001:", get_attendance("S001", "DBMS"))
    print("\nAll marks for S001:", get_marks("S001"))

    complaint_id = file_complaint("S001", "hostel", "Water supply has been cut off for 3 days")
    print(f"\nFiled test complaint, id={complaint_id}")