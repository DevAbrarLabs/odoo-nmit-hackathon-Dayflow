#Odoo NMIT Hackathon
"""
Authentication & Role-Based Access System (single file, SQLite-backed)
--------------------------------------------------------------------------
Flow:
  1. Database tables are created automatically in the background
     (init_db runs once when the program starts - you never see this,
     it just makes sure users.db is ready).
  2. You see a menu: Register / Login / Exit.
  3. At Login, you first choose which role you're logging in as
     (Employee / HR / Admin). Admin accounts require an extra PIN
     on top of the password.
  4. On successful Login, ALL of your personal info is shown on screen
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
            role TEXT NOT NULL,
            admin_pin_hash TEXT
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
# Password / PIN hashing + validation helpers
# ==========================================================================
def hash_password(password: str) -> str:
    salt = "static_salt_demo"  # in production use a unique random salt per user
    return hashlib.sha256((salt + password).encode()).hexdigest()


def hash_pin(pin: str) -> str:
    salt = "static_pin_salt_demo"  # in production use a unique random salt per user
    return hashlib.sha256((salt + pin).encode()).hexdigest()


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


def validate_pin(pin: str) -> list:
    errors = []
    if not re.fullmatch(r"\d{4,6}", pin):
        errors.append("Admin PIN must be 4 to 6 digits.")
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

    # Admin accounts need an extra PIN, set once at registration time.
    pin_hash = None
    if role_input == "Admin":
        pin = input("Set an Admin PIN (4-6 digits): ").strip()
        confirm_pin = input("Confirm Admin PIN: ").strip()

        pin_errors = validate_pin(pin)
        if pin != confirm_pin:
            errors.append("Admin PINs do not match.")
        errors.extend(pin_errors)

        if pin == confirm_pin and not pin_errors:
            pin_hash = hash_pin(pin)

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
        "INSERT INTO users (employee_id, email, password_hash, role, admin_pin_hash) "
        "VALUES (?, ?, ?, ?, ?)",
        (employee_id, email, hash_password(password), role_input, pin_hash),
    )
    conn.commit()
    conn.close()

    print(f"\nRegistration successful! You can now log in as {email}.")


# ==========================================================================
# 3) LOGIN -> choose role -> verify credentials -> show personal info -> dashboard
# ==========================================================================
def login():
    print("\n--- Login ---")
    print("1. Employee")
    print("2. HR")
    print("3. Admin")
    role_choice = input("Login as (1-3): ").strip()

    role_map = {"1": "Employee", "2": "HR", "3": "Admin"}
    selected_role = role_map.get(role_choice)

    if not selected_role:
        print("\nError: Please choose 1, 2, or 3.")
        return

    email = input("Email: ").strip().lower()
    password = input("Password: ").strip()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT employee_id, password_hash, role, admin_pin_hash FROM users WHERE email = ?",
        (email,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        print("\nError: No account found with that email.")
        return

    employee_id, stored_hash, actual_role, stored_pin_hash = row

    if hash_password(password) != stored_hash:
        print("\nError: Incorrect password.")
        return

    # The role picked at the login screen must match the account's actual role.
    if selected_role != actual_role:
        print(f"\nError: This account is registered as '{actual_role}', "
              f"not '{selected_role}'.")
        return

    # Admin accounts require the extra PIN check.
    if actual_role == "Admin":
        pin = input("Admin PIN: ").strip()
        if not stored_pin_hash or hash_pin(pin) != stored_pin_hash:
            print("\nError: Incorrect Admin PIN.")
            return

    print(f"\nLogin successful. Welcome, {employee_id} ({actual_role})!")

    show_personal_info(employee_id, email, actual_role)

    if actual_role == "Admin":
        admin_dashboard()
    else:
        employee_dashboard(employee_id, actual_role)


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


# ==========================================================================
# ADMIN DASHBOARD - full access
# ==========================================================================
def admin_dashboard():
    while True:
        print("\n===== Admin Dashboard =====")
        print("1. Manage employees")
        print("2. Approve / reject leave requests")
        print("3. Approve / reject attendance")
        print("4. View payroll details (all employees)")
        print("5. Add / update payroll record")
        print("6. Logout")
        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            manage_employees()
        elif choice == "2":
            approve_leave_requests()
        elif choice == "3":
            approve_attendance()
        elif choice == "4":
            view_all_payroll()
        elif choice == "5":
            add_or_update_payroll()
        elif choice == "6":
            print("Logged out.")
            break
        else:
            print("Invalid option. Please choose 1-6.")


def manage_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, email, role FROM users ORDER BY role, employee_id")
    rows = cursor.fetchall()

    if not rows:
        print("No employees registered yet.")
        conn.close()
        return

    print("\n--- All Employees ---")
    for emp_id, email, role in rows:
        print(f"  {emp_id:<12} {email:<30} {role}")

    remove = input("\nEnter Employee ID to remove (or press Enter to skip): ").strip()
    if remove:
        cursor.execute("SELECT 1 FROM users WHERE employee_id = ?", (remove,))
        if not cursor.fetchone():
            print(f"Error: No employee found with ID '{remove}'.")
        else:
            cursor.execute("DELETE FROM users WHERE employee_id = ?", (remove,))
            conn.commit()
            print(f"Employee '{remove}' removed.")

    conn.close()


def approve_leave_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, employee_id, reason FROM leave_requests WHERE status = 'Pending'")
    rows = cursor.fetchall()

    if not rows:
        print("No pending leave requests.")
        conn.close()
        return

    print("\n--- Pending Leave Requests ---")
    for req_id, emp_id, reason in rows:
        print(f"  [{req_id}] {emp_id} - {reason}")

    req_id = input("\nEnter request ID to review (or press Enter to skip): ").strip()
    if req_id:
        decision = input("Approve or Reject (A/R): ").strip().upper()
        if decision not in ("A", "R"):
            print("Error: Enter 'A' to approve or 'R' to reject.")
        else:
            new_status = "Approved" if decision == "A" else "Rejected"
            cursor.execute(
                "UPDATE leave_requests SET status = ? WHERE id = ?", (new_status, req_id)
            )
            conn.commit()
            print(f"Leave request {req_id} marked as {new_status}.")

    conn.close()


def approve_attendance():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, employee_id, date, status FROM attendance WHERE approval_status = 'Pending'"
    )
    rows = cursor.fetchall()

    if not rows:
        print("No pending attendance entries.")
        conn.close()
        return

    print("\n--- Pending Attendance ---")
    for att_id, emp_id, date, status in rows:
        print(f"  [{att_id}] {emp_id} - {date} - {status}")

    att_id = input("\nEnter attendance ID to review (or press Enter to skip): ").strip()
    if att_id:
        decision = input("Approve or Reject (A/R): ").strip().upper()
        if decision not in ("A", "R"):
            print("Error: Enter 'A' to approve or 'R' to reject.")
        else:
            new_status = "Approved" if decision == "A" else "Rejected"
            cursor.execute(
                "UPDATE attendance SET approval_status = ? WHERE id = ?", (new_status, att_id)
            )
            conn.commit()
            print(f"Attendance {att_id} marked as {new_status}.")

    conn.close()


def view_all_payroll():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id, salary, month FROM payroll ORDER BY employee_id")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No payroll records yet.")
        return

    print("\n--- Payroll (All Employees) ---")
    for emp_id, salary, month in rows:
        print(f"  {emp_id:<12} {month:<10} {salary:.2f}")


def add_or_update_payroll():
    emp_id = input("Employee ID: ").strip()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE employee_id = ?", (emp_id,))
    if not cursor.fetchone():
        print(f"Error: No employee found with ID '{emp_id}'.")
        conn.close()
        return

    salary_input = input("Salary: ").strip()
    try:
        salary = float(salary_input)
    except ValueError:
        print("Error: Salary must be a number.")
        conn.close()
        return

    month = input("Month (e.g. 2026-08): ").strip()
    if not month:
        print("Error: Month is required.")
        conn.close()
        return

    cursor.execute("SELECT 1 FROM payroll WHERE employee_id = ?", (emp_id,))
    if cursor.fetchone():
        cursor.execute(
            "UPDATE payroll SET salary = ?, month = ? WHERE employee_id = ?",
            (salary, month, emp_id),
        )
        print(f"Payroll updated for {emp_id}.")
    else:
        cursor.execute(
            "INSERT INTO payroll (employee_id, salary, month) VALUES (?, ?, ?)",
            (emp_id, salary, month),
        )
        print(f"Payroll record created for {emp_id}.")

    conn.commit()
    conn.close()


# ==========================================================================
# MAIN MENU - Register / Login / Exit
# ==========================================================================
def main():
    init_db()  # background setup, runs once, no output shown
    while True:
        print("\n===== Menu =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
