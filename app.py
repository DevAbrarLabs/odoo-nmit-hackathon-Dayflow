"""NovaHR — dependency-free Python + SQLite HR dashboard demo."""
from __future__ import annotations

import hashlib
import html
import os
import re
import secrets
import sqlite3
from datetime import date, datetime
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
DB_FILE = Path(os.environ.get("NOVAHR_DB", ROOT / "novahr.db"))
SESSIONS: dict[str, str] = {}

ACCOUNTS = [
    ("EMP001", "Aarav Mehta", "employee@novahr.demo", "Employee@123", "Employee", None, 72000),
    ("EMP002", "Riya Sharma", "riya@novahr.demo", "Riya@1234", "Employee", None, 68000),
    ("EMP003", "Kabir Rao", "kabir@novahr.demo", "Kabir@1234", "Employee", None, 75500),
    ("EMP004", "Ananya Iyer", "ananya@novahr.demo", "Ananya@123", "Employee", None, 81000),
    ("EMP005", "Vihaan Nair", "vihaan@novahr.demo", "Vihaan@123", "Employee", None, 64500),
    ("HR001", "Neha Kapoor", "hr@novahr.demo", "HR@123456", "HR", None, 93000),
    ("HR002", "Arjun Menon", "arjun.hr@novahr.demo", "ArjunHR@123", "HR", None, 88500),
    ("ADM001", "Meera Singh", "admin@novahr.demo", "Admin@123", "Admin", "4826", 125000),
    ("ADM002", "Dev Malhotra", "dev.admin@novahr.demo", "DevAdmin@123", "Admin", "7319", 118000),
]


def digest(value: str, salt: str) -> str:
    return hashlib.sha256((salt + value).encode()).hexdigest()


class ClosingConnection(sqlite3.Connection):
    """SQLite connection that also closes when its context manager exits."""
    def __exit__(self, exc_type, exc_value, traceback):
        result = super().__exit__(exc_type, exc_value, traceback)
        self.close()
        return result


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_FILE, factory=ClosingConnection)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db


def init_db() -> None:
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          employee_id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('Employee','HR','Admin')),
          pin_hash TEXT
        );
        CREATE TABLE IF NOT EXISTS attendance(
          id INTEGER PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES users(employee_id),
          date TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('Present','Absent')),
          approval_status TEXT NOT NULL DEFAULT 'Approved', UNIQUE(employee_id,date)
        );
        CREATE TABLE IF NOT EXISTS leave_requests(
          id INTEGER PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES users(employee_id),
          date_from TEXT NOT NULL, date_to TEXT NOT NULL, leave_type TEXT NOT NULL,
          reason TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending'
            CHECK(status IN ('Pending','Approved','Rejected')),
          submitted_at TEXT NOT NULL, reviewed_by TEXT REFERENCES users(employee_id), reviewed_at TEXT,
          CHECK(date_to >= date_from)
        );
        CREATE TABLE IF NOT EXISTS payroll(
          id INTEGER PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES users(employee_id),
          month TEXT NOT NULL, basic REAL NOT NULL CHECK(basic BETWEEN 10000 AND 1000000),
          hra REAL NOT NULL CHECK(hra>=0 AND hra<=basic),
          allowances REAL NOT NULL CHECK(allowances>=0 AND allowances<=basic),
          deductions REAL NOT NULL CHECK(deductions>=0 AND deductions<=basic+hra+allowances),
          net_salary REAL GENERATED ALWAYS AS (basic+hra+allowances-deductions) STORED,
          updated_at TEXT NOT NULL, updated_by TEXT NOT NULL, UNIQUE(employee_id,month)
        );
        CREATE INDEX IF NOT EXISTS idx_leave_pending ON leave_requests(status,submitted_at);
        CREATE INDEX IF NOT EXISTS idx_leave_employee ON leave_requests(employee_id,submitted_at);
        CREATE INDEX IF NOT EXISTS idx_attendance_employee_date ON attendance(employee_id,date);
        CREATE INDEX IF NOT EXISTS idx_payroll_month_employee ON payroll(month,employee_id);
        """)
        if db.execute("SELECT count(*) FROM users").fetchone()[0]:
            return
        for i, (eid, name, email, password, role, pin, salary) in enumerate(ACCOUNTS):
            db.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", (
                eid, name, email, digest(password, "novahr_password_"), role,
                digest(pin, "novahr_pin_") if pin else None,
            ))
            for day in range(11, 16):
                status = "Absent" if day == 14 and i % 3 == 0 else "Present"
                db.execute("INSERT INTO attendance(employee_id,date,status) VALUES(?,?,?)",
                           (eid, f"2026-08-{day:02d}", status))
            db.execute("""INSERT INTO payroll
              (employee_id,month,basic,hra,allowances,deductions,updated_at,updated_by)
              VALUES(?,?,?,?,?,?,?,?)""", (eid, "2026-08", salary, round(salary*.2),
              round(salary*.08), round(salary*.05), "2026-08-01T09:00:00", "System"))
        samples = [
            ("EMP001","2026-09-03","2026-09-05","Annual leave","Family celebration","Pending"),
            ("EMP002","2026-08-28","2026-08-28","Personal leave","Appointment","Pending"),
            ("EMP003","2026-09-12","2026-09-16","Annual leave","Travel","Approved"),
        ]
        for eid, start, end, kind, reason, status in samples:
            db.execute("""INSERT INTO leave_requests
              (employee_id,date_from,date_to,leave_type,reason,status,submitted_at)
              VALUES(?,?,?,?,?,?,?)""", (eid,start,end,kind,reason,status,"2026-08-22T10:00:00"))
        db.execute("PRAGMA optimize")


CSS = """
:root{--bg:#07111f;--panel:#101d30;--line:#263950;--text:#eef5ff;--muted:#9db0c8;--accent:#6c8cff;--accent2:#38d7ca;--bad:#ff7685;--good:#49d69b}*{box-sizing:border-box}body{margin:0;font:14px/1.45 Segoe UI,sans-serif;background:radial-gradient(circle at 15% 0,#172c50 0,transparent 35%),var(--bg);color:var(--text)}body.admin{--accent:#aa78ff;--accent2:#ffbd62;background:radial-gradient(circle at 15% 0,#38245d 0,transparent 38%),#090b18}a{text-decoration:none;color:inherit}.login{min-height:100vh;display:grid;place-items:center;padding:24px}.login-card,.card{background:linear-gradient(145deg,#111f33,#0d1929);border:1px solid var(--line);border-radius:18px;padding:22px}.login-card{width:min(460px,100%);padding:34px}.brand{font-size:21px;font-weight:800}.brand b{display:inline-grid;place-items:center;width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#06111d;margin-right:10px}.layout{min-height:100vh;display:grid;grid-template-columns:245px 1fr}.side{background:#0b1726dd;border-right:1px solid var(--line);padding:24px 18px;display:flex;flex-direction:column;gap:28px}.admin .side{background:#110e23ee}.nav{display:grid;gap:7px}.nav a{padding:11px 14px;border-radius:11px;color:var(--muted);font-weight:700}.nav a:hover,.nav a.active{background:#192a43;color:white}.badge{float:right;background:#ff735f;color:white;border-radius:99px;padding:1px 7px;font-size:11px}.spacer{flex:1}.user{padding:13px;border-radius:13px;background:#13233a}.user small{display:block;color:var(--muted)}main{padding:32px;overflow:auto}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.top h1{margin:0;font-size:28px}.pill,.status{padding:6px 10px;border-radius:99px;background:#173a39;color:#7af1cf}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.stat strong{display:block;font-size:26px;margin-top:8px}.muted{color:var(--muted)}.section{margin-top:18px}.split{display:grid;grid-template-columns:1.2fr .8fr;gap:16px}.cols{display:grid;grid-template-columns:1fr 1fr;gap:12px}label{display:block;margin:14px 0 6px;font-weight:600}input,select{width:100%;padding:11px 13px;border:1px solid var(--line);background:#091522;color:white;border-radius:10px}button{border:0;border-radius:10px;padding:10px 14px;font-weight:700;cursor:pointer}.primary{background:linear-gradient(135deg,var(--accent),#586cdb);color:white}.approve{background:#164435;color:#83f2bd}.reject{background:#48252c;color:#ffabb4}.danger{background:#46242c;color:#ffbdc3;padding:10px 14px}.flash{padding:12px 16px;border:1px solid #317460;background:#143d35;border-radius:11px;margin-bottom:16px}.error{background:#43242b;border-color:#7d3743}.status.pending{background:#41361b;color:#ffd77a}.status.rejected{background:#41242a;color:#ff9ca6}table{width:100%;border-collapse:collapse}th,td{padding:12px;text-align:left;border-bottom:1px solid var(--line)}th{color:var(--muted);font-size:12px;text-transform:uppercase}.table{overflow:auto}.actions{display:flex;gap:7px}.eyebrow{color:var(--accent2);font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:12px}@media(max-width:900px){.layout{grid-template-columns:1fr}.side{border-right:0}.nav{grid-template-columns:repeat(3,1fr)}.grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:620px){main{padding:20px}.grid,.split,.cols{grid-template-columns:1fr}.nav{grid-template-columns:1fr 1fr}.top{align-items:flex-start}}
"""


def e(value: object) -> str:
    return html.escape(str(value))


def money(value: float) -> str:
    return "₹" + f"{value:,.0f}"


def leave_days(start: str, end: str) -> int:
    """Return inclusive calendar days in a validated leave range."""
    return (date.fromisoformat(end) - date.fromisoformat(start)).days + 1


def page(title: str, body: str, user=None, active="", flash="") -> str:
    if not user:
        return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>{e(title)} · NovaHR</title><style>{CSS}</style></head><body>{body}</body></html>"
    admin = user["role"] == "Admin"
    with connect() as db:
        pending = db.execute("SELECT count(*) FROM leave_requests WHERE status='Pending'").fetchone()[0]
    links = [("/", "⌂ Home", "home"), ("/attendance", "◷ Attendance", "attendance"),
             ("/leave", "▣ My leave", "leave"), ("/payroll", "₹ Payroll", "payroll")]
    if admin:
        links[2] = ("/admin/leaves", f"🔔 Leave approvals <span class='badge'>{pending}</span>", "leaves")
        links.append(("/admin", "⚙ Administration", "admin"))
    nav = "".join(f"<a class='{'active' if active==key else ''}' href='{url}'>{label}</a>" for url,label,key in links)
    alert = f"<div class='flash'>{e(flash)}</div>" if flash else ""
    shell = f"""<div class='layout'><aside class='side'><div class='brand'><b>N</b>{'NovaHR Command' if admin else 'NovaHR'}</div><nav class='nav'>{nav}</nav><div class='spacer'></div><div class='user'><strong>{e(user['name'])}</strong><small>{e(user['employee_id'])} · {e(user['role'])}</small></div><a class='danger' href='/logout'>Sign out</a></aside><main><div class='top'><div><h1>{e(title)}</h1><div class='muted'>{'Administrator workspace' if admin else 'Personal employee workspace'}</div></div><span class='pill'>{e(user['role'])}</span></div>{alert}{body}</main></div>"""
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'><title>{e(title)} · NovaHR</title><style>{CSS}</style></head><body class='{'admin' if admin else ''}'>{shell}</body></html>"


class NovaHRHandler(BaseHTTPRequestHandler):
    def user(self):
        jar = cookies.SimpleCookie(self.headers.get("Cookie"))
        token = jar.get("novahr_session")
        eid = SESSIONS.get(token.value) if token else None
        if not eid: return None
        with connect() as db: return db.execute("SELECT * FROM users WHERE employee_id=?",(eid,)).fetchone()

    def form(self):
        length = int(self.headers.get("Content-Length", 0))
        return {k:v[0] for k,v in parse_qs(self.rfile.read(length).decode()).items()}

    def send_html(self, text, status=200, cookie=None):
        data=text.encode(); self.send_response(status); self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        if cookie: self.send_header("Set-Cookie",cookie)
        self.end_headers(); self.wfile.write(data)

    def redirect(self, location, cookie=None):
        self.send_response(303); self.send_header("Location",location)
        if cookie: self.send_header("Set-Cookie",cookie)
        self.end_headers()

    def require_user(self, admin=False):
        user=self.user()
        if not user: self.redirect("/login"); return None
        if admin and user["role"]!="Admin": self.send_html(page("Forbidden","<div class='card'>Admin access required.</div>",user),403); return None
        return user

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/login":
            created="<div class='flash'>Employee account created. You can sign in now.</div>" if parse_qs(urlparse(self.path).query).get("created") else ""
            form=f"""<section class='login'><div class='login-card'><div class='brand'><b>N</b>NovaHR</div><h1>Welcome back</h1><p class='muted'>Sign in to your Python-powered HR workspace.</p>{created}<form method='post' action='/login'><label>Role</label><select name='role'><option>Employee</option><option>HR</option><option>Admin</option></select><label>Email</label><input name='email' value='admin@novahr.demo' required><label>Password</label><input type='password' name='password' value='Admin@123' required><label>Admin PIN (admin only)</label><input type='password' name='pin' value='4826'><p><button class='primary' type='submit'>Sign in</button></p></form><p>New employee? <a class='pill' href='/signup'>Create an account</a></p><p class='muted'>Admin demo: admin@novahr.demo · Admin@123 · PIN 4826</p></div></section>"""
            return self.send_html(page("Sign in",form))
        if path=="/signup":
            form="""<section class='login'><div class='login-card'><div class='brand'><b>N</b>NovaHR</div><h1>Create employee account</h1><p class='muted'>New accounts are always created with Employee permissions.</p><form method='post' action='/signup'><label>Full name</label><input name='name' maxlength='80' required><label>Email</label><input type='email' name='email' maxlength='120' required><label>Password</label><input type='password' name='password' minlength='8' required><label>Confirm password</label><input type='password' name='confirm_password' minlength='8' required><p class='muted'>Use at least 8 characters with uppercase, lowercase, and a number.</p><p><button class='primary' type='submit'>Create employee account</button></p></form><p><a class='pill' href='/login'>Back to sign in</a></p></div></section>"""
            return self.send_html(page("Create account",form))
        if path=="/logout":
            jar=cookies.SimpleCookie(self.headers.get("Cookie")); token=jar.get("novahr_session")
            if token: SESSIONS.pop(token.value,None)
            return self.redirect("/login","novahr_session=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax")
        user=self.require_user(path.startswith("/admin"))
        if not user: return
        with connect() as db:
            if path=="/":
                pay=db.execute("SELECT * FROM payroll WHERE employee_id=? ORDER BY month DESC",(user["employee_id"],)).fetchone()
                attendance=db.execute("SELECT count(*),sum(status='Present') FROM attendance WHERE employee_id=?",(user["employee_id"],)).fetchone()
                if user["role"]=="Admin":
                    people=db.execute("SELECT count(*) FROM users").fetchone()[0]; pending=db.execute("SELECT count(*) FROM leave_requests WHERE status='Pending'").fetchone()[0]; total=db.execute("SELECT sum(net_salary) FROM payroll").fetchone()[0]
                    body=f"<div class='eyebrow'>Administrator command center</div><div class='grid'><div class='card stat'><span class='muted'>People</span><strong>{people}</strong></div><div class='card stat'><span class='muted'>New leave alerts</span><strong>{pending}</strong></div><div class='card stat'><span class='muted'>Monthly payroll</span><strong>{money(total)}</strong></div><div class='card stat'><span class='muted'>System</span><strong>Healthy</strong></div></div><div class='card section'><h2>Approval queue</h2><p class='muted'>Employees have submitted leave requests that need your decision.</p><a class='primary' href='/admin/leaves'>Review {pending} notifications</a></div>"
                else:
                    rate=round((attendance[1] or 0)/(attendance[0] or 1)*100); leaves=db.execute("SELECT count(*) FROM leave_requests WHERE employee_id=?",(user["employee_id"],)).fetchone()[0]
                    body=f"<div class='eyebrow'>Employee workspace</div><div class='grid'><div class='card stat'><span class='muted'>My attendance</span><strong>{rate}%</strong></div><div class='card stat'><span class='muted'>My leave requests</span><strong>{leaves}</strong></div><div class='card stat'><span class='muted'>My net payroll</span><strong>{money(pay['net_salary']) if pay else '—'}</strong></div><div class='card stat'><span class='muted'>Profile</span><strong>Active</strong></div></div>"
                return self.send_html(page("Home",body,user,"home"))
            if path=="/attendance":
                rows=db.execute("SELECT * FROM attendance WHERE employee_id=? ORDER BY date DESC",(user["employee_id"],)).fetchall()
                trs="".join(f"<tr><td>{e(r['date'])}</td><td>{e(r['status'])}</td><td>{e(r['approval_status'])}</td></tr>" for r in rows)
                return self.send_html(page("Attendance",f"<div class='card table'><table><tr><th>Date</th><th>Status</th><th>Approval</th></tr>{trs}</table></div>",user,"attendance"))
            if path=="/leave":
                rows=db.execute("""SELECT l.*,u.name reviewer FROM leave_requests l LEFT JOIN users u ON u.employee_id=l.reviewed_by WHERE l.employee_id=? ORDER BY l.id DESC""",(user["employee_id"],)).fetchall()
                trs="".join(f"<tr><td>{e(r['date_from'])}</td><td>{e(r['date_to'])}</td><td>{leave_days(r['date_from'],r['date_to'])}</td><td>{e(r['leave_type'])}</td><td>{e(r['reason'])}</td><td><span class='status {r['status'].lower()}'>{e(r['status'])}</span></td><td>{e(r['reviewer'] or 'Awaiting review')}</td></tr>" for r in rows)
                body=f"""<div class='split'><div class='card'><h2>Apply for multiple days</h2><p class='muted'>Use the calendar buttons to choose the first and last day of your leave.</p><form method='post' action='/leave'><div class='cols'><div><label>Starting day</label><input id='leave-start' type='date' name='date_from' required></div><div><label>Ending day</label><input id='leave-end' type='date' name='date_to' required></div></div><div id='range-summary' class='flash section'>Choose a starting day and ending day.</div><label>Leave type</label><select name='leave_type'><option>Annual leave</option><option>Sick leave</option><option>Personal leave</option></select><label>Reason</label><input name='reason' maxlength='120' required><p><button class='primary'>Submit leave request</button></p></form></div><div class='card'><h2>How the calendar works</h2><p class='muted'>1. Select your starting day.<br><br>2. Select your ending day.<br><br>3. Check the full range and total days.<br><br>4. Submit to notify the admin.</p></div></div><div class='card table section'><h2>My requests</h2><table><tr><th>Starting day</th><th>Ending day</th><th>Total days</th><th>Type</th><th>Reason</th><th>Status</th><th>Reviewer</th></tr>{trs}</table></div><script>const start=document.getElementById('leave-start'),end=document.getElementById('leave-end'),summary=document.getElementById('range-summary');function showRange(){{if(start.value)end.min=start.value;if(!start.value||!end.value){{summary.textContent='Choose a starting day and ending day.';return}}if(end.value<start.value){{summary.textContent='Ending day must be on or after the starting day.';return}}const a=new Date(start.value+'T00:00:00'),b=new Date(end.value+'T00:00:00'),days=Math.round((b-a)/86400000)+1;summary.textContent=`Selected: ${{start.value}} to ${{end.value}} · ${{days}} calendar day${{days===1?'':'s'}}`;}}start.addEventListener('change',showRange);end.addEventListener('change',showRange);</script>"""
                return self.send_html(page("My leave",body,user,"leave"))
            if path=="/payroll":
                if user["role"]=="Admin":
                    rows=db.execute("SELECT p.*,u.name FROM payroll p JOIN users u USING(employee_id) ORDER BY u.name").fetchall()
                    trs="".join(f"<tr><td>{e(r['name'])}<div class='muted'>{e(r['employee_id'])}</div></td><td>{e(r['month'])}</td><td>{money(r['basic'])}</td><td>{money(r['hra'])}</td><td>{money(r['allowances'])}</td><td>{money(r['deductions'])}</td><td><strong>{money(r['net_salary'])}</strong></td><td><a class='primary' href='/admin/payroll?employee={e(r['employee_id'])}'>Edit</a></td></tr>" for r in rows)
                    body=f"<div class='card table'><table><tr><th>Employee</th><th>Month</th><th>Basic</th><th>HRA</th><th>Allowances</th><th>Deductions</th><th>Net</th><th></th></tr>{trs}</table></div>"
                else:
                    r=db.execute("SELECT * FROM payroll WHERE employee_id=? ORDER BY month DESC",(user["employee_id"],)).fetchone(); body="<div class='card'>No payroll record.</div>" if not r else f"<div class='card'><h2>{e(r['month'])} salary</h2><table><tr><td>Basic</td><td>{money(r['basic'])}</td></tr><tr><td>HRA</td><td>{money(r['hra'])}</td></tr><tr><td>Allowances</td><td>{money(r['allowances'])}</td></tr><tr><td>Deductions</td><td>− {money(r['deductions'])}</td></tr><tr><th>Net salary</th><th>{money(r['net_salary'])}</th></tr></table></div>"
                return self.send_html(page("Payroll",body,user,"payroll"))
            if path=="/admin/leaves":
                rows=db.execute("SELECT l.*,u.name FROM leave_requests l JOIN users u USING(employee_id) ORDER BY (l.status='Pending') DESC,l.id DESC").fetchall()
                trs="".join(f"<tr><td>{e(r['name'])}<div class='muted'>{e(r['employee_id'])}</div></td><td>{e(r['date_from'])}</td><td>{e(r['date_to'])}</td><td>{leave_days(r['date_from'],r['date_to'])}</td><td>{e(r['leave_type'])}</td><td>{e(r['reason'])}</td><td><span class='status {r['status'].lower()}'>{e(r['status'])}</span></td><td>{self.leave_actions(r)}</td></tr>" for r in rows)
                pending=sum(r["status"]=="Pending" for r in rows)
                return self.send_html(page("Leave approvals",f"<div class='flash'>🔔 {pending} new leave notifications</div><div class='card table'><table><tr><th>Employee</th><th>Starting day</th><th>Ending day</th><th>Days</th><th>Type</th><th>Reason</th><th>Status</th><th>Decision</th></tr>{trs}</table></div>",user,"leaves"))
            if path=="/admin/payroll":
                eid=parse_qs(urlparse(self.path).query).get("employee",[""])[0]; r=db.execute("SELECT p.*,u.name FROM payroll p JOIN users u USING(employee_id) WHERE employee_id=?",(eid,)).fetchone()
                if not r: return self.send_html(page("Not found","<div class='card'>Payroll not found.</div>",user),404)
                body=f"""<div class='card'><h2>{e(r['name'])} · {e(eid)}</h2><form method='post' action='/admin/payroll'><input type='hidden' name='employee_id' value='{e(eid)}'><div class='cols'><div><label>Month</label><input name='month' value='{e(r['month'])}' required></div><div><label>Basic</label><input type='number' name='basic' value='{r['basic']}' required></div><div><label>HRA</label><input type='number' name='hra' value='{r['hra']}' required></div><div><label>Allowances</label><input type='number' name='allowances' value='{r['allowances']}' required></div><div><label>Deductions</label><input type='number' name='deductions' value='{r['deductions']}' required></div></div><p><button class='primary'>Validate and save</button></p></form></div>"""
                return self.send_html(page("Update salary structure",body,user,"payroll"))
            if path=="/admin":
                return self.send_html(page("Administration","<div class='card'><h2>Admin permissions</h2><p class='muted'>Review all leave requests, manage payroll structures, and view workforce information.</p></div>",user,"admin"))
        self.send_html(page("Not found","<div class='card'>Page not found.</div>",user),404)

    def leave_actions(self, row):
        if row["status"] != "Pending": return "<span class='muted'>Reviewed</span>"
        return f"""<div class='actions'><form method='post' action='/admin/leaves'><input type='hidden' name='request_id' value='{row['id']}'><button class='approve' name='decision' value='Approved'>Approve</button><button class='reject' name='decision' value='Rejected'>Deny</button></form></div>"""

    def do_POST(self):
        path=urlparse(self.path).path; data=self.form()
        if path=="/signup":
            name=data.get("name","").strip(); email=data.get("email","").strip().lower(); password=data.get("password",""); confirm=data.get("confirm_password","")
            errors=[]
            if len(name)<2: errors.append("Enter your full name.")
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email): errors.append("Enter a valid email address.")
            if len(password)<8 or not re.search(r"[A-Z]",password) or not re.search(r"[a-z]",password) or not re.search(r"\d",password): errors.append("Password must have 8 characters, uppercase, lowercase, and a number.")
            if password!=confirm: errors.append("Passwords do not match.")
            with connect() as db:
                if db.execute("SELECT 1 FROM users WHERE lower(email)=lower(?)",(email,)).fetchone(): errors.append("An account already uses this email.")
                if not errors:
                    numbers=[int(r[0][3:]) for r in db.execute("SELECT employee_id FROM users WHERE employee_id GLOB 'EMP[0-9]*'") if r[0][3:].isdigit()]
                    employee_id=f"EMP{max(numbers,default=0)+1:03d}"
                    db.execute("INSERT INTO users(employee_id,name,email,password_hash,role,pin_hash) VALUES(?,?,?,?,?,NULL)",(employee_id,name,email,digest(password,"novahr_password_"),"Employee"))
            if errors:
                return self.send_html(page("Account not created","<section class='login'><div class='login-card error'><h1>Check your details</h1><p>"+"<br>".join(map(e,errors))+"</p><a class='pill' href='/signup'>Try again</a></div></section>"),400)
            return self.redirect("/login?created=1")
        if path=="/login":
            with connect() as db: user=db.execute("SELECT * FROM users WHERE lower(email)=lower(?)",(data.get("email",""),)).fetchone()
            valid=user and secrets.compare_digest(user["password_hash"],digest(data.get("password",""),"novahr_password_")) and user["role"]==data.get("role")
            if valid and user["role"]=="Admin": valid=bool(user["pin_hash"] and secrets.compare_digest(user["pin_hash"],digest(data.get("pin",""),"novahr_pin_")))
            if not valid: return self.send_html(page("Sign in failed","<section class='login'><div class='login-card'><h1>Sign in failed</h1><p class='muted'>Check the email, password, selected role, and admin PIN.</p><a class='primary' href='/login'>Try again</a></div></section>"),401)
            token=secrets.token_urlsafe(32); SESSIONS[token]=user["employee_id"]
            return self.redirect("/",f"novahr_session={token}; Path=/; HttpOnly; SameSite=Lax")
        user=self.require_user(path.startswith("/admin"))
        if not user: return
        if path=="/leave":
            start,end=data.get("date_from",""),data.get("date_to",""); reason=data.get("reason","").strip()
            if not start or not end or end<start or not reason: return self.send_html(page("Invalid leave","<div class='card'>Check the dates and reason.</div>",user,"leave"),400)
            with connect() as db: db.execute("""INSERT INTO leave_requests(employee_id,date_from,date_to,leave_type,reason,submitted_at) VALUES(?,?,?,?,?,?)""",(user["employee_id"],start,end,data.get("leave_type","Annual leave"),reason,datetime.now().isoformat(timespec="seconds")))
            return self.redirect("/leave")
        if path=="/admin/leaves":
            decision=data.get("decision"); request_id=data.get("request_id")
            if decision not in ("Approved","Rejected"): return self.send_html(page("Invalid decision","<div class='card'>Invalid decision.</div>",user),400)
            with connect() as db: db.execute("""UPDATE leave_requests SET status=?,reviewed_by=?,reviewed_at=? WHERE id=? AND status='Pending'""",(decision,user["employee_id"],datetime.now().isoformat(timespec="seconds"),request_id))
            return self.redirect("/admin/leaves")
        if path=="/admin/payroll":
            try:
                eid=data["employee_id"]; month=data["month"]; basic=float(data["basic"]); hra=float(data["hra"]); allowances=float(data["allowances"]); deductions=float(data["deductions"])
                errors=[]
                if not (10000<=basic<=1000000): errors.append("Basic must be between ₹10,000 and ₹10,00,000.")
                if min(hra,allowances,deductions)<0: errors.append("Salary values cannot be negative.")
                if hra>basic or allowances>basic: errors.append("HRA and allowances cannot exceed basic salary.")
                if deductions>basic+hra+allowances: errors.append("Deductions cannot exceed gross salary.")
                if len(month)!=7 or month[4]!="-": errors.append("Month must use YYYY-MM.")
                if errors: return self.send_html(page("Payroll validation failed","<div class='card error'>"+"<br>".join(map(e,errors))+"</div>",user,"payroll"),400)
                with connect() as db: db.execute("""UPDATE payroll SET month=?,basic=?,hra=?,allowances=?,deductions=?,updated_at=?,updated_by=? WHERE employee_id=?""",(month,basic,hra,allowances,deductions,datetime.now().isoformat(timespec="seconds"),user["name"],eid))
                return self.redirect("/payroll")
            except (KeyError,ValueError,sqlite3.IntegrityError):
                return self.send_html(page("Payroll validation failed","<div class='card error'>Invalid salary structure.</div>",user,"payroll"),400)
        self.send_html(page("Not found","<div class='card'>Page not found.</div>",user),404)

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")


if __name__ == "__main__":
    init_db()
    port=int(os.environ.get("NOVAHR_PORT","8000"))
    print(f"NovaHR is running at http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),NovaHRHandler).serve_forever()
