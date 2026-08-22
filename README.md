# Odoo-Nmit-Hackathon
import re
import sqlite3
import hashlib

DB_FILE = "users.db"


# --------------------------------------------------------------------------
# Database setup
# --------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# --------------------------------------------------------------------------
# Password hashing (never store plain text passwords)
# --------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = "static_salt_demo"  # in production use a unique random salt per user
    return hashlib.sha256((salt + password).encode()).hexdigest()


# --------------------------------------------------------------------------
# Validation rules
# --------------------------------------------------------------------------
def validate_email(email: str) -> bool:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> list:
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")
    return errors
    # --------------------------------------------------------------------------
# Register (Sign Up)
# --------------------------------------------------------------------------
def register():
    print("\n--- Register ---")
    employee_id = input("Employee ID: ").strip()
    email = input("Email: ").strip().lower()
    password = input("Password: ").strip()
    confirm_password = input("Confirm Password: ").strip()
    role = input("Role (Employee/HR): ").strip().capitalize()

    errors = []

    if not employee_id:
        errors.append("Employee ID is required.")
    if not validate_email(email):
        errors.append("Invalid email format.")
    if role not in ("Employee", "Hr"):
        errors.append("Role must be 'Employee' or 'HR'.")
    else:
        role = "HR" if role == "Hr" else role
    if password != confirm_password:
        errors.append("Passwords do not match.")

    errors.extend(validate_password(password))

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE employee_id = ?", (employee_id,))
    if cursor.fetchone():
        errors.append("Employee ID already registered.")

    cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        errors.append("Email already registered.")

    if errors:
        print("\nRegistration failed:")
        for e in errors:
            print(f"  - {e}")
        conn.close()
        return

    cursor.execute(
        "INSERT INTO users (employee_id, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (employee_id, email, hash_password(password), role),
    )
    conn.commit()
    conn.close()

    print(f"\nRegistration successful! You can now log in as {email}.")

