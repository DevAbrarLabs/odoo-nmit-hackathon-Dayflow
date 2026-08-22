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
