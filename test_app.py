import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import app


class NovaHRTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        app.DB_FILE = Path(self.tmp.name) / "test.db"
        app.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_sample_counts(self):
        with app.connect() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM users").fetchone()[0], 9)
            self.assertEqual(db.execute("SELECT count(*) FROM attendance").fetchone()[0], 45)
            self.assertEqual(db.execute("SELECT count(*) FROM payroll").fetchone()[0], 9)
            self.assertEqual(db.execute("SELECT count(*) FROM leave_requests").fetchone()[0], 3)

    def test_leave_approval_flow(self):
        with app.connect() as db:
            cur = db.execute("""INSERT INTO leave_requests
              (employee_id,date_from,date_to,leave_type,reason,submitted_at)
              VALUES('EMP001','2026-10-01','2026-10-02','Annual leave','Trip','2026-09-01')""")
            request_id = cur.lastrowid
            self.assertEqual(db.execute("SELECT status FROM leave_requests WHERE id=?",(request_id,)).fetchone()[0], "Pending")
            db.execute("UPDATE leave_requests SET status='Approved',reviewed_by='ADM001' WHERE id=?",(request_id,))
            row=db.execute("SELECT status,reviewed_by FROM leave_requests WHERE id=?",(request_id,)).fetchone()
            self.assertEqual(tuple(row),("Approved","ADM001"))

    def test_multiple_day_leave_count(self):
        self.assertEqual(app.leave_days("2026-10-01", "2026-10-05"), 5)

    def test_invalid_payroll_is_blocked(self):
        with self.assertRaises(sqlite3.IntegrityError):
            with app.connect() as db:
                db.execute("UPDATE payroll SET deductions=9999999 WHERE employee_id='EMP001'")


if __name__ == "__main__":
    unittest.main()
