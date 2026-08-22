#Odoo NMIT Hackathon
"""
Authentication & Role-Based Access System (single file, SQLite-backed)
--------------------------------------------------------------------------
Flow:
  1. Database tables are created automatically in the background
     (init_db runs once when the program starts - you never see this,
     it just makes sure users.db is ready).
  2. You see a menu: Register / Login / Exit.
  3. On successful Login, ALL of your personal info is shown on screen
     first, then you're taken to your dashboard (Employee/HR vs Admin).

Roles: Employee, HR, Admin

Run with:
    python auth_system.py
"""

import re
import sqlite3
import hashlib

DB_FILE = "users.db"


# ==========================================================================
# 1) DATABASE SETUP - runs quietly in the background before the menu shows
# ==========================================================================
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            approval_status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            salary REAL NOT NULL,
            month TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_connection():
    return sqlite3.connect(DB_FILE)


# ==========================================================================
# Password hashing + validation helpers
# ==========================================================================
def hash_password(password: str) -> str:
    salt = "static_salt_demo"  # in production use a unique random salt per user
    return hashlib.sha256((salt + password).encode()).hexdigest()


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


VALID_ROLES = ("Employee", "HR", "Admin")


# ==========================================================================
# 2) REGISTER
# ==========================================================================
def register():
    print("\n--- Register ---")
    employee_id = input("Employee ID: ").strip()
    email = input("Email: ").strip().lower()
    password = input("Password: ").strip()
    confirm_password = input("Confirm Password: ").strip()
    role_input = input("Role (Employee/HR/Admin): ").strip().capitalize()

    errors = []

    if not employee_id:
        errors.append("Employee ID is required.")
    if not validate_email(email):
        errors.append("Invalid email format.")
    if role_input not in VALID_ROLES:
        errors.append("Role must be 'Employee', 'HR', or 'Admin'.")
    if password != confirm_password:
        errors.append("Passwords do not match.")

    errors.extend(validate_password(password))

    conn = get_connection()
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
        (employee_id, email, hash_password(password), role_input),
    )
    conn.commit()
    conn.close()

    print(f"\nRegistration successful! You can now log in as {email}.")


# ==========================================================================
# 3) LOGIN -> show personal info -> route to dashboard
# ==========================================================================
def login():
    print("\n--- Login ---")
    email = input("Email: ").strip().lower()
    password = input("Password: ").strip()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT employee_id, password_hash, role FROM users WHERE email = ?",
        (email,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print("\nError: No account found with that email.")
        return

    employee_id, stored_hash, role = row

    if hash_password(password) != stored_hash:
        print("\nError: Incorrect password.")
        return

    print(f"\nLogin successful. Welcome, {employee_id} ({role})!")

    show_personal_info(employee_id, email, role)

    if role == "Admin":
        admin_dashboard()
    else:
        employee_dashboard(employee_id, role)


def show_personal_info(employee_id, email, role):
    """Displays all of the logged-in user's personal info on screen."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT salary, month FROM payroll WHERE employee_id = ?", (employee_id,))
    payroll_row = cursor.fetchone()
    conn.close()

    print("\n========== YOUR INFO ==========")
    print(f" Employee ID : {employee_id}")
    print(f" Email       : {email}")
    print(f" Role        : {role}")
    if payroll_row:
        salary, month = payroll_row
        print(f" Payroll     : {salary:.2f} ({month})")
    else:
        print(" Payroll     : No record on file yet")
    print("================================\n")


# ==========================================================================
# EMPLOYEE / HR DASHBOARD
# ==========================================================================
def employee_dashboard(employee_id, role):
    while True:
        print(f"\n===== {role} Dashboard ({employee_id}) =====")
        print("1. Apply for leave")
        print("2. Mark attendance")
        print("3. View my payroll")
        print("4. Logout")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            apply_leave(employee_id)
        elif choice == "2":
            mark_attendance(employee_id)
        elif choice == "3":
            view_my_payroll(employee_id)
        elif choice == "4":
            print("Logged out.")
            break
        else:
            print("Invalid option. Please choose 1-4.")


def apply_leave(employee_id):
    reason = input("Reason for leave: ").strip()
    if not reason:
        print("Error: Reason cannot be empty.")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leave_requests (employee_id, reason, status) VALUES (?, ?, 'Pending')",
        (employee_id, reason),
    )
    conn.commit()
    conn.close()
    print("Leave request submitted. Awaiting Admin approval.")


def mark_attendance(employee_id):
    date = input("Date (YYYY-MM-DD): ").strip()
    status = input("Status (Present/Absent): ").strip().capitalize()
    if status not in ("Present", "Absent"):
        print("Error: Status must be 'Present' or 'Absent'.")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (employee_id, date, status, approval_status) VALUES (?, ?, ?, 'Pending')",
        (employee_id, date, status),
    )
    conn.commit()
    conn.close()
    print("Attendance submitted. Awaiting Admin approval.")


def view_my_payroll(employee_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT salary, month FROM payroll WHERE employee_id = ?", (employee_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print("No payroll record found yet. Contact Admin.")
        return
    salary, month = row
    print(f"\nPayroll for {month}: {salary:.2f}")
