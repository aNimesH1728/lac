import bcrypt
from db import get_connection


def hash_password(plain_password: str) -> str:
    
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def login(roll_number: str, password: str):
    """
    Returns the student's record (as a dict) if credentials are valid, else None.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE roll_number = ?", (roll_number,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None  

    if not verify_password(password, row["password_hash"]):
        return None  

    return dict(row)


if __name__ == "__main__":
    
    test_roll = "123CS0216"
    test_pass = "testpass123"

    result = login(test_roll, test_pass)
    if result:
        print(f"Login succeeded: {result['name']}, semester {result['semester']}")
    else:
        print("Login failed (expected if seed.py hasn't been run yet, or wrong test credentials)")