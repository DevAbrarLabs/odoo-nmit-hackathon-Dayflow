"""
============================================================
 Dayflow HRMS — Admin Console (Python / Streamlit port)

 Ported 1:1 from the static site (index.html + styles.css +
 data.js + app.js): same seed-data rules, same 7 admin pages,
 same design system (ink navy + paper + sunrise-gold, Space
 Grotesk / Inter / IBM Plex Mono). Hash routing -> sidebar nav.
 localStorage -> a local JSON file (dayflow_store.json).
============================================================
"""

import json
import os
from datetime import datetime, timedelta
import random

import pandas as pd
import streamlit as st

# ============================================================
# Design tokens (mirrors styles.css :root)
# ============================================================

INK = "#14213D"
INK_2 = "#1C2C51"
INK_3 = "#29396A"
PAPER = "#F6F5F1"
CARD = "#FFFFFF"
LINE = "#E3E1D9"
TEXT = "#1B1C20"
TEXT_MUTED = "#6C6F76"
TEXT_FAINT = "#9A9DA4"
GOLD = "#E3A93C"
GOLD_DEEP = "#C6871C"
GOLD_BG = "#FBF0DA"
GREEN = "#2F8558"
GREEN_BG = "#E4F3EB"
RED = "#C13F3F"
RED_BG = "#FBEAEA"
BLUE = "#3B5EA8"
BLUE_BG = "#EAF0FA"

BADGE_STYLE = {
    "Present": (GREEN, GREEN_BG), "Approved": (GREEN, GREEN_BG),
    "Absent": (RED, RED_BG), "Rejected": (RED, RED_BG),
    "Half-day": (GOLD_DEEP, GOLD_BG),
    "Leave": (BLUE, BLUE_BG), "Pending": (BLUE, BLUE_BG),
}
CHART_COLOR = {"Present": GREEN, "Absent": RED, "Half-day": GOLD, "Leave": BLUE,
               "Approved": GREEN, "Rejected": RED, "Pending": BLUE}

# ============================================================
# Data constants (mirrors data.js)
# ============================================================

DEPARTMENTS = ["Engineering", "Human Resources", "Sales", "Marketing", "Finance", "Operations"]

DESIGNATIONS = {
    "Engineering": ["Software Engineer", "Senior Engineer", "Engineering Manager"],
    "Human Resources": ["HR Executive", "HR Manager"],
    "Sales": ["Sales Associate", "Sales Manager"],
    "Marketing": ["Marketing Executive", "Marketing Manager"],
    "Finance": ["Accountant", "Finance Manager"],
    "Operations": ["Operations Executive", "Operations Manager"],
}

LEAVE_TYPES = ["Paid", "Sick", "Unpaid"]
ATTENDANCE_STATUSES = ["Present", "Absent", "Half-day", "Leave"]

FIRST_NAMES = ["Aarav", "Vivaan", "Isha", "Ananya", "Kabir", "Diya", "Reyansh", "Myra",
               "Arjun", "Saanvi", "Vihaan", "Anika", "Rohan", "Priya", "Karthik", "Neha"]
LAST_NAMES = ["Sharma", "Verma", "Iyer", "Gupta", "Nair", "Reddy", "Menon", "Kapoor",
              "Joshi", "Rao", "Pillai", "Chowdhury", "Mehta", "Bose", "Das", "Singh"]

STORE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dayflow_store.json")

NAV = [
    ("dashboard", "Admin Dashboard"),
    ("employees", "Employee List"),
    ("employee-details", "Employee Details"),
    ("attendance", "Attendance Overview"),
    ("leave", "Leave Approvals"),
    ("payroll", "Payroll Management"),
    ("analytics", "Analytics & Reports"),
]


# ============================================================
# Seed-data generation (mirrors generateSeedData in data.js)
# ============================================================

def _iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def _weighted_status() -> str:
    r = random.random() * 100
    if r < 78:
        return "Present"
    if r < 84:
        return "Absent"
    if r < 94:
        return "Half-day"
    return "Leave"


def generate_seed_data(num_employees: int = 24, attendance_days: int = 45) -> dict:
    today = datetime.now()
    employees = []
    for i in range(1, num_employees + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        dept = random.choice(DEPARTMENTS)
        designation = random.choice(DESIGNATIONS[dept])
        basic = random.choice([28000, 35000, 42000, 55000, 68000, 82000])
        join_date = today - timedelta(days=random.randint(60, 1500))
        employees.append({
            "id": i, "employeeCode": f"DF{1000 + i}", "name": f"{first} {last}",
            "email": f"{first.lower()}.{last.lower()}{i}@dayflow.com",
            "role": "Admin" if i == 1 else "Employee",
            "department": dept, "designation": designation, "phone": "", "address": "",
            "joinDate": _iso(join_date), "basicSalary": basic,
            "hra": round(basic * 0.4), "allowances": round(basic * 0.15), "deductions": round(basic * 0.08),
        })

    attendance = []
    att_id = 1
    for emp in employees:
        for d in range(attendance_days):
            day = today - timedelta(days=d)
            if day.weekday() in (5, 6):
                continue
            status = _weighted_status()
            attendance.append({
                "id": att_id, "employeeId": emp["id"], "date": _iso(day), "status": status,
                "checkIn": f"09:1{random.randint(0, 9)}" if status == "Present" else None,
                "checkOut": f"18:0{random.randint(0, 9)}" if status == "Present" else None,
            })
            att_id += 1

    leave_requests = []
    sample = random.sample(employees, min(10, len(employees)))
    remarks_pool = ["Family function", "Not feeling well", "Personal work", "Travel"]
    status_pool = ["Pending", "Pending", "Approved", "Rejected"]
    for idx, emp in enumerate(sample):
        start = today - timedelta(days=random.randint(0, 20))
        end = start + timedelta(days=random.randint(0, 3))
        leave_requests.append({
            "id": idx + 1, "employeeId": emp["id"], "leaveType": random.choice(LEAVE_TYPES),
            "startDate": _iso(start), "endDate": _iso(end),
            "remarks": random.choice(remarks_pool), "status": random.choice(status_pool), "adminComment": "",
        })

    return {"employees": employees, "attendance": attendance, "leaveRequests": leave_requests}


def load_store() -> dict:
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    seeded = generate_seed_data()
    save_store(seeded)
    return seeded


def save_store(store: dict) -> None:
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)


def reset_store() -> dict:
    if os.path.exists(STORE_PATH):
        os.remove(STORE_PATH)
    return load_store()


# ============================================================
# Helpers (mirrors the top of app.js)
# ============================================================

def fmt_money(n) -> str:
    return "₹" + f"{round(n):,}"


def net_salary(e: dict) -> float:
    return e["basicSalary"] + e["hra"] + e["allowances"] - e["deductions"]


def esc(s) -> str:
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def badge(status: str) -> str:
    color, bg = BADGE_STYLE.get(status, (TEXT_MUTED, "#eee"))
    return (f'<span class="df-badge" style="color:{color}; background:{bg};">'
            f'<i style="background:{color}"></i>{esc(status)}</span>')


def initials(name: str) -> str:
    parts = name.split(" ")
    return "".join(p[0] for p in parts[:2]).upper()


def get_employee(store: dict, emp_id) -> dict | None:
    emp_id = int(emp_id)
    for e in store["employees"]:
        if e["id"] == emp_id:
            return e
    return None


def days_ago_iso(n: int) -> str:
    return _iso(datetime.now() - timedelta(days=n))


def attendance_in_range(store: dict, days: int) -> list:
    since = days_ago_iso(days)
    return [a for a in store["attendance"] if a["date"] >= since]


def to_csv_bytes(rows: list, columns: list) -> bytes:
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=[k for k, _ in columns])
    keys = [k for k, _ in columns]
    labels = [lbl for _, lbl in columns]
    df = df.reindex(columns=keys)
    df.columns = labels
    return df.to_csv(index=False).encode("utf-8")


# ---------------- Design-matched HTML renderers ----------------

def card_open(title: str | None = None, extra_style: str = "") -> str:
    html = f'<div class="df-card" style="{extra_style}">'
    if title:
        html += f'<div class="df-card-title">{esc(title)}</div>'
    return html


CARD_CLOSE = "</div>"


def page_header(title: str, subtitle: str):
    st.markdown(
        f'<div class="df-page-header"><div><h1 class="df-page-title">{esc(title)}</h1>'
        f'<div class="df-page-sub">{esc(subtitle)}</div></div>{workday_arc_svg()}</div>',
        unsafe_allow_html=True,
    )


def workday_arc_svg() -> str:
    now = datetime.now()
    start_h, end_h = 9, 18
    frac = min(1, max(0, ((now.hour + now.minute / 60) - start_h) / (end_h - start_h)))
    w, h = 150, 26
    x0, x1 = 6, w - 6
    mid_y, top_y = h - 6, 4
    cx = (x0 + x1) / 2
    dot_x = x0 + (x1 - x0) * frac
    t = frac
    dot_y = (1 - t) ** 2 * mid_y + 2 * (1 - t) * t * top_y + t * t * mid_y
    before_sunset = start_h <= now.hour < end_h
    label = (f"Workday · {round(frac * 100)}% through" if before_sunset
             else ("Before workday" if now.hour < start_h else "Workday complete"))
    return f"""
    <div class="df-arc-wrap" title="{esc(label)}">
      <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
        <path d="M{x0} {mid_y} Q {cx} {top_y} {x1} {mid_y}" fill="none" stroke="{LINE}" stroke-width="2" stroke-linecap="round"/>
        <path d="M{x0} {mid_y} Q {cx} {top_y} {dot_x} {dot_y}" fill="none" stroke="{GOLD}" stroke-width="2" stroke-linecap="round"/>
        <circle cx="{dot_x}" cy="{dot_y}" r="3.4" fill="{GOLD}"/>
      </svg>
      <span class="df-arc-label">{esc(label)}</span>
    </div>"""


def metric_grid(items: list):
    """items: list of (label, value) — renders the .grid-4 metric-card row."""
    cols_html = "".join(
        f'<div class="df-card df-metric-card"><div class="df-metric-label">{esc(lbl)}</div>'
        f'<div class="df-metric-value">{val}</div></div>' for lbl, val in items
    )
    st.markdown(f'<div class="df-grid" style="grid-template-columns:repeat({len(items)},1fr);">{cols_html}</div>',
                unsafe_allow_html=True)


def bar_list(data: list, max_value=None, value_fmt=None):
    if not data:
        st.markdown('<div class="df-empty">No data.</div>', unsafe_allow_html=True)
        return
    m = max_value or max(1, max(d["value"] for d in data))
    fmt = value_fmt or (lambda v: v)
    rows_html = ""
    for d in data:
        pct = max(2, (d["value"] / m) * 100) if m else 2
        color = d.get("color", GOLD)
        rows_html += (
            f'<div class="df-bar-row"><div class="df-bar-label">{esc(d["label"])}</div>'
            f'<div class="df-bar-track"><div class="df-bar-fill" style="width:{pct}%; background:{color};"></div></div>'
            f'<div class="df-bar-value">{esc(str(fmt(d["value"])))}</div></div>'
        )
    st.markdown(f'<div>{rows_html}</div>', unsafe_allow_html=True)


def html_table(rows: list, columns: list, badge_cols=(), mono_cols=(), code_cols=()):
    """columns: list of (key, label). Renders a real .df-table, badges included."""
    if not rows:
        st.markdown('<div class="df-empty">No rows to show.</div>', unsafe_allow_html=True)
        return
    thead = "".join(f"<th>{esc(lbl)}</th>" for _, lbl in columns)
    body_rows = ""
    for r in rows:
        cells = ""
        for key, _ in columns:
            v = r.get(key, "")
            if key in badge_cols:
                cells += f"<td>{badge(v)}</td>"
            elif key in mono_cols:
                cells += f'<td class="mono">{esc(v if v not in (None, "") else "—")}</td>'
            elif key in code_cols:
                cells += f'<td class="df-emp-code">{esc(v)}</td>'
            else:
                cells += f"<td>{esc(v)}</td>"
        body_rows += f"<tr>{cells}</tr>"
    st.markdown(
        f'<div class="df-table-wrap"><table class="df-table"><thead><tr>{thead}</tr></thead>'
        f'<tbody>{body_rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# Global CSS (mirrors styles.css, adapted to Streamlit's DOM)
# ============================================================

def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {{
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  color: {TEXT};
}}
.stApp {{ background: {PAPER}; }}
.block-container {{ padding: 30px 38px 60px; max-width: 1180px; }}

h1, h2, h3 {{ font-family: "Space Grotesk", "Inter", sans-serif !important; font-weight: 600 !important;
  letter-spacing: -0.01em; color: {INK} !important; }}
.mono {{ font-family: "IBM Plex Mono", monospace; }}
::selection {{ background: {GOLD_BG}; color: {INK}; }}

/* ---- Sidebar (brand block) ---- */
section[data-testid="stSidebar"] {{
  background: {INK};
}}
section[data-testid="stSidebar"] * {{ color: #E7E9F2; }}
.df-brand {{ display:flex; align-items:center; gap:10px; padding: 6px 4px 18px 4px;
  border-bottom: 1px solid rgba(255,255,255,0.09); margin-bottom: 12px; }}
.df-brand-name {{ font-family:"Space Grotesk",sans-serif; font-weight:700; font-size:18px; color:#fff; line-height:1; }}
.df-brand-tag {{ font-size:11px; color:#9AA4C4; margin-top:2px; }}
.df-sidebar-foot {{ border-top: 1px solid rgba(255,255,255,0.09); padding-top:14px; margin-top:14px;
  font-size:12px; color:#8E97B5; }}
.df-sidebar-foot strong {{ color:#DCE1F0; }}

/* Style the nav radio to look like the original .nav-item list */
section[data-testid="stSidebar"] div[role="radiogroup"] {{ gap: 2px; }}
section[data-testid="stSidebar"] div[role="radiogroup"] label {{
  padding: 10px 12px; border-radius: 6px; width: 100%;
}}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background: {INK_2}; }}
section[data-testid="stSidebar"] div[role="radiogroup"] label div:first-child {{ display: none; }}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {{
  font-size: 13.5px !important; font-weight: 500 !important; color: #B9C0D6 !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"] {{
  background: transparent; border: 1px solid rgba(255,255,255,0.18); color: #DCE1F0 !important;
}}

/* ---- Page header / workday arc ---- */
.df-page-header {{ display:flex; justify-content:space-between; align-items:flex-end; gap:24px; margin-bottom:20px; }}
.df-page-title {{ font-size:26px !important; margin:0 !important; }}
.df-page-sub {{ color:{TEXT_MUTED}; font-size:13.5px; margin-top:4px; }}
.df-arc-wrap {{ display:flex; align-items:center; gap:10px; min-width:220px; }}
.df-arc-label {{ font-family:"IBM Plex Mono",monospace; font-size:11px; color:{TEXT_MUTED}; white-space:nowrap; }}

/* ---- Cards / grid / metrics ---- */
.df-grid {{ display:grid; gap:16px; margin-bottom: 20px; }}
.df-card {{ background:{CARD}; border:1px solid {LINE}; border-radius:10px;
  box-shadow: 0 1px 2px rgba(20,33,61,0.06), 0 1px 1px rgba(20,33,61,0.04); padding:20px 22px; }}
.df-card-title {{ font-family:"Space Grotesk",sans-serif; font-size:15px; font-weight:600; color:{INK}; margin:0 0 14px 0; }}
.df-metric-card {{ padding: 18px 20px; }}
.df-metric-label {{ font-size:12px; color:{TEXT_MUTED}; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:8px; }}
.df-metric-value {{ font-family:"Space Grotesk",sans-serif; font-size:26px; font-weight:700; color:{INK}; }}

/* ---- Tables ---- */
.df-table-wrap {{ overflow-x:auto; }}
table.df-table {{ width:100%; border-collapse:collapse; font-size:13.5px; }}
table.df-table thead th {{ text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:0.05em;
  color:{TEXT_MUTED}; font-weight:600; padding:0 12px 10px 12px; border-bottom:1px solid {LINE}; white-space:nowrap; }}
table.df-table tbody td {{ padding:11px 12px; border-bottom:1px solid {LINE}; color:{TEXT}; white-space:nowrap; }}
table.df-table tbody tr:last-child td {{ border-bottom:none; }}
table.df-table tbody tr:hover {{ background:#FBFAF7; }}
.df-emp-code {{ font-family:"IBM Plex Mono",monospace !important; color:{TEXT_MUTED}; font-size:12.5px; }}

/* ---- Badges ---- */
.df-badge {{ display:inline-flex; align-items:center; gap:5px; padding:3px 10px; border-radius:999px;
  font-size:11.5px; font-weight:600; font-family:"IBM Plex Mono",monospace; letter-spacing:0.01em; }}
.df-badge i {{ width:6px; height:6px; border-radius:50%; display:inline-block; }}

/* ---- Bar list ---- */
.df-bar-row {{ display:grid; grid-template-columns:130px 1fr 60px; align-items:center; gap:10px; margin-bottom:9px; font-size:12.5px; }}
.df-bar-label {{ color:{TEXT}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.df-bar-track {{ background:#EFEDE6; border-radius:5px; height:10px; overflow:hidden; }}
.df-bar-fill {{ height:100%; border-radius:5px; }}
.df-bar-value {{ text-align:right; font-family:"IBM Plex Mono",monospace; color:{TEXT_MUTED}; font-size:12px; }}

/* ---- Misc ---- */
.df-empty {{ padding:34px 20px; text-align:center; color:{TEXT_MUTED}; font-size:13.5px; }}
.df-req-card {{ border:1px solid {LINE}; border-radius:10px; padding:16px 18px; margin-bottom:12px; background:#fff; }}
.df-req-name {{ font-weight:600; color:{INK}; }}
.df-req-meta {{ font-size:12.5px; color:{TEXT_MUTED}; margin-top:2px; }}
.df-avatar-circle {{ width:52px; height:52px; border-radius:50%; background:{INK}; color:{GOLD};
  display:flex; align-items:center; justify-content:center; font-family:"Space Grotesk",sans-serif;
  font-weight:700; font-size:18px; flex-shrink:0; }}
.df-slip-box {{ font-family:"IBM Plex Mono",monospace; font-size:12.5px; background:{INK}; color:#D8DEEF;
  padding:18px 20px; border-radius:10px; white-space:pre; line-height:1.6; overflow-x:auto; }}

/* ---- Native widgets, retinted to match the palette ---- */
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
  background:{INK} !important; border-color:{INK} !important; color:#fff !important; border-radius:6px !important;
}}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{ background:{INK_3} !important; }}
.stButton > button[kind="secondary"] {{ border-radius:6px !important; }}
div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"], div[data-baseweb="base-input"] {{
  border-radius:6px !important;
}}
div[data-baseweb="tab-highlight"] {{ background-color:{GOLD} !important; }}
div[data-baseweb="tab"] p {{ font-weight:600 !important; }}
[data-testid="stMetricValue"] {{ font-family:"Space Grotesk",sans-serif; color:{INK}; }}
hr {{ border-color: {LINE} !important; }}
</style>
    """, unsafe_allow_html=True)


# ============================================================
# App bootstrap
# ============================================================

st.set_page_config(page_title="Dayflow HRMS — Admin Console", layout="wide", page_icon="🗓️")
inject_css()

if "store" not in st.session_state:
    st.session_state.store = load_store()
if "el_search" not in st.session_state:
    st.session_state.el_search = ""

store = st.session_state.store


def commit():
    save_store(store)


# ---------------- Sidebar ----------------

with st.sidebar:
    st.markdown("""
    <div class="df-brand">
      <svg width="30" height="30" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="15" stroke="#E3A93C" stroke-width="1.4"/>
        <path d="M4 18 A12 12 0 0 0 28 18" stroke="#E3A93C" stroke-width="1.6" fill="none" stroke-linecap="round"/>
        <circle cx="16" cy="8.2" r="2.6" fill="#E3A93C"/>
      </svg>
      <div><div class="df-brand-name">Dayflow</div><div class="df-brand-tag">Admin Console</div></div>
    </div>
    """, unsafe_allow_html=True)

    route_labels = [label for _, label in NAV]
    route_ids = [rid for rid, _ in NAV]
    choice = st.radio("Navigate", route_labels, label_visibility="collapsed")
    route = route_ids[route_labels.index(choice)]

    st.markdown(
        f'<div class="df-sidebar-foot">Signed in as <strong>HR Admin</strong><br>'
        f'{datetime.now().strftime("%A, %d %B")}</div>',
        unsafe_allow_html=True,
    )
    if st.button("🔄 Reset demo data", use_container_width=True):
        st.session_state.store = reset_store()
        st.rerun()


# ============================================================
# PAGE: Admin Dashboard
# ============================================================

def render_dashboard():
    emp = store["employees"]
    today = days_ago_iso(0)
    today_att = [a for a in store["attendance"] if a["date"] == today]
    pending_leaves = [l for l in store["leaveRequests"] if l["status"] == "Pending"]
    present_today = len([a for a in today_att if a["status"] == "Present"])
    total_payroll = sum(net_salary(e) for e in emp)

    page_header("Admin Dashboard", "A snapshot of today across the organization.")

    metric_grid([
        ("Total Employees", len(emp)),
        ("Present Today", present_today),
        ("Pending Leave Requests", len(pending_leaves)),
        ("Monthly Payroll (est.)", f'<span class="mono">{fmt_money(total_payroll)}</span>'),
    ])

    col1, col2 = st.columns([1.35, 1])
    with col1:
        st.markdown(card_open("Department Distribution"), unsafe_allow_html=True)
        dept_counts: dict = {}
        for e in emp:
            dept_counts[e["department"]] = dept_counts.get(e["department"], 0) + 1
        dept_data = sorted([{"label": k, "value": v, "color": GOLD} for k, v in dept_counts.items()],
                            key=lambda d: -d["value"])
        bar_list(dept_data)
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    with col2:
        st.markdown(card_open("Recent Leave Requests"), unsafe_allow_html=True)
        recent_leave = sorted(store["leaveRequests"], key=lambda l: l["status"] != "Pending")[:5]
        if not recent_leave:
            st.markdown('<div class="df-empty">No leave requests yet.</div>', unsafe_allow_html=True)
        else:
            html = ""
            for r in recent_leave:
                e = get_employee(store, r["employeeId"])
                html += (
                    f'<div style="margin-bottom:14px;">'
                    f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                    f'<strong style="font-size:13.5px;">{esc(e["name"])}</strong>{badge(r["status"])}</div>'
                    f'<div class="df-req-meta">{esc(e["department"])} · {esc(r["leaveType"])} leave</div>'
                    f'<div class="df-req-meta mono">{r["startDate"]} → {r["endDate"]}</div></div>'
                )
            st.markdown(html, unsafe_allow_html=True)
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(card_open("Today's Attendance Snapshot"), unsafe_allow_html=True)
    if today_att:
        rows = []
        for a in today_att:
            e = get_employee(store, a["employeeId"])
            rows.append({"name": e["name"], "department": e["department"], "status": a["status"],
                         "checkIn": a["checkIn"], "checkOut": a["checkOut"]})
        html_table(rows, [("name", "Name"), ("department", "Department"), ("status", "Status"),
                           ("checkIn", "Check-in"), ("checkOut", "Check-out")],
                   badge_cols=("status",), mono_cols=("checkIn", "checkOut"))
    else:
        st.markdown('<div class="df-empty">No attendance logged yet for today.</div>', unsafe_allow_html=True)
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)


# ============================================================
# PAGE: Employee List
# ============================================================

def render_employee_list():
    page_header("Employee List", "Browse, search, and manage every employee in the organization.")

    depts = ["All"] + sorted(set(e["department"] for e in store["employees"]))
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("Search", value=st.session_state.el_search,
                                placeholder="Search by name, email, or employee code")
        st.session_state.el_search = search
    with c2:
        dept_filter = st.selectbox("Department", depts)
    with c3:
        role_filter = st.selectbox("Role", ["All", "Employee", "Admin"])

    rows = store["employees"]
    s = search.lower().strip()
    if s:
        rows = [e for e in rows if s in e["name"].lower() or s in e["email"].lower()
                or s in e["employeeCode"].lower()]
    if dept_filter != "All":
        rows = [e for e in rows if e["department"] == dept_filter]
    if role_filter != "All":
        rows = [e for e in rows if e["role"] == role_filter]

    st.markdown(f'<div class="df-page-sub" style="margin-bottom:10px;">Showing <strong>{len(rows)}</strong> '
                f'of <strong>{len(store["employees"])}</strong> employees</div>', unsafe_allow_html=True)
    st.markdown(card_open(), unsafe_allow_html=True)
    html_table(
        [{"employeeCode": e["employeeCode"], "name": e["name"], "email": e["email"],
          "department": e["department"], "designation": e["designation"], "role": e["role"],
          "joinDate": e["joinDate"]} for e in rows],
        [("employeeCode", "Emp code"), ("name", "Name"), ("email", "Email"), ("department", "Department"),
         ("designation", "Designation"), ("role", "Role"), ("joinDate", "Joined")],
        code_cols=("employeeCode",), mono_cols=("joinDate",),
    )
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    if rows:
        options = {f'{e["name"]} ({e["employeeCode"]})': e["id"] for e in rows}
        pick = st.selectbox("Open employee details for…", ["—"] + list(options.keys()))
        if pick != "—":
            st.session_state.jump_employee_id = options[pick]
            st.session_state.route_override = "employee-details"
            st.rerun()

    st.divider()
    with st.expander("➕ Add new employee"):
        with st.form("add_emp_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            name = fc1.text_input("Full name")
            email = fc2.text_input("Email")
            fc3, fc4 = st.columns(2)
            dept = fc3.selectbox("Department", DEPARTMENTS, key="add_emp_dept")
            designation = fc4.selectbox("Designation", DESIGNATIONS[dept], key="add_emp_designation")
            fc5, fc6 = st.columns(2)
            basic = fc5.number_input("Basic salary (₹)", min_value=0, step=1000, value=30000)
            role = fc6.selectbox("Role", ["Employee", "Admin"])
            submitted = st.form_submit_button("Add employee", type="primary")

            if submitted:
                if not name.strip() or not email.strip():
                    st.warning("Name and email are required.")
                elif any(e["email"].lower() == email.strip().lower() for e in store["employees"]):
                    st.error("An employee with that email already exists.")
                else:
                    next_id = max(e["id"] for e in store["employees"]) + 1
                    store["employees"].append({
                        "id": next_id, "employeeCode": f"DF{1000 + next_id}", "name": name.strip(),
                        "email": email.strip(), "role": role, "department": dept, "designation": designation,
                        "phone": "", "address": "", "joinDate": _iso(datetime.now()), "basicSalary": int(basic),
                        "hra": round(basic * 0.4), "allowances": round(basic * 0.15), "deductions": round(basic * 0.08),
                    })
                    commit()
                    st.success(f"Added {name.strip()}.")
                    st.rerun()


# ============================================================
# PAGE: Employee Details
# ============================================================

def render_employee_details():
    page_header("Employee Details", "Full profile, salary structure, and history for one employee.")

    emp = store["employees"]
    if not emp:
        st.markdown('<div class="df-empty">No employees yet.</div>', unsafe_allow_html=True)
        return

    options = {f'{x["name"]} ({x["employeeCode"]})': x["id"] for x in emp}
    jump_id = st.session_state.pop("jump_employee_id", None) if "jump_employee_id" in st.session_state else None
    default_index = 0
    if jump_id is not None:
        ids = list(options.values())
        if jump_id in ids:
            default_index = ids.index(jump_id)
    label = st.selectbox("Select an employee", list(options.keys()), index=default_index)
    e = get_employee(store, options[label])

    att = sorted([a for a in store["attendance"] if a["employeeId"] == e["id"]],
                 key=lambda a: a["date"], reverse=True)[:14]
    lv = sorted([l for l in store["leaveRequests"] if l["employeeId"] == e["id"]],
                key=lambda l: l["startDate"], reverse=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(card_open(), unsafe_allow_html=True)
        st.markdown(
            f'<div style="display:flex; align-items:center; gap:16px; margin-bottom:6px;">'
            f'<div class="df-avatar-circle">{initials(e["name"])}</div>'
            f'<div><h3 style="margin:0;">{esc(e["name"])}</h3>'
            f'<div class="df-page-sub" style="margin-top:2px;">{esc(e["designation"])} · {esc(e["department"])}</div></div></div>',
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(
            f'<div style="font-size:13.5px; line-height:2;">'
            f'<div><span class="df-metric-label" style="display:inline;">Emp code&nbsp;</span> <span class="mono">{esc(e["employeeCode"])}</span></div>'
            f'<div><span class="df-metric-label" style="display:inline;">Role&nbsp;</span> {esc(e["role"])}</div>'
            f'<div><span class="df-metric-label" style="display:inline;">Joined&nbsp;</span> <span class="mono">{e["joinDate"]}</span></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    with col2:
        st.markdown(card_open(), unsafe_allow_html=True)
        tab_profile, tab_salary, tab_history = st.tabs(["Profile", "Salary structure", "Attendance & leave"])

        with tab_profile:
            with st.form("edit_profile_form"):
                pc1, pc2 = st.columns(2)
                email = pc1.text_input("Email", value=e["email"])
                phone = pc2.text_input("Phone", value=e.get("phone", ""))
                address = st.text_area("Address", value=e.get("address", ""))
                pc3, pc4 = st.columns(2)
                new_dept = pc3.selectbox("Department", DEPARTMENTS, index=DEPARTMENTS.index(e["department"]))
                desig_opts = DESIGNATIONS[new_dept]
                desig_index = desig_opts.index(e["designation"]) if e["designation"] in desig_opts else 0
                new_desig = pc4.selectbox("Designation", desig_opts, index=desig_index)
                if st.form_submit_button("Save changes (Admin)", type="primary"):
                    e["email"] = email
                    e["phone"] = phone
                    e["address"] = address
                    e["department"] = new_dept
                    e["designation"] = new_desig
                    commit()
                    st.success("Profile updated.")
                    st.rerun()

        with tab_salary:
            st.markdown('<div class="df-metric-label">Net monthly salary</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="df-metric-value mono" style="margin-bottom:16px; font-size:24px;">'
                        f'{fmt_money(net_salary(e))}</div>', unsafe_allow_html=True)
            metric_grid([("Basic", fmt_money(e["basicSalary"])), ("HRA", fmt_money(e["hra"])),
                         ("Allowances", fmt_money(e["allowances"])), ("Deductions", fmt_money(e["deductions"]))])

        with tab_history:
            st.markdown('<div class="df-card-title">Last 14 attendance entries</div>', unsafe_allow_html=True)
            html_table(att, [("date", "Date"), ("status", "Status"), ("checkIn", "Check-in"), ("checkOut", "Check-out")],
                       badge_cols=("status",), mono_cols=("date", "checkIn", "checkOut"))
            st.divider()
            st.markdown('<div class="df-card-title">Leave history</div>', unsafe_allow_html=True)
            html_table(lv, [("leaveType", "Type"), ("startDate", "From"), ("endDate", "To"),
                             ("status", "Status"), ("remarks", "Remarks")],
                       badge_cols=("status",), mono_cols=("startDate", "endDate"))
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)


# ============================================================
# PAGE: Attendance Overview
# ============================================================

def render_attendance():
    page_header("Attendance Overview", "Company-wide attendance across all employees.")

    depts = ["All"] + sorted(set(e["department"] for e in store["employees"]))
    c1, c2, c3 = st.columns(3)
    with c1:
        days = st.slider("Show last N days", 1, 45, 14)
    with c2:
        dept_filter = st.selectbox("Department", depts, key="att_dept")
    with c3:
        status_filter = st.selectbox("Status", ["All"] + ATTENDANCE_STATUSES, key="att_status")

    rows = attendance_in_range(store, days)
    rows = [a for a in rows if (dept_filter == "All" or get_employee(store, a["employeeId"])["department"] == dept_filter)
            and (status_filter == "All" or a["status"] == status_filter)]
    rows.sort(key=lambda a: a["date"], reverse=True)

    st.markdown(card_open("Status breakdown (filtered range)"), unsafe_allow_html=True)
    counts = {s: 0 for s in ATTENDANCE_STATUSES}
    for a in rows:
        counts[a["status"]] += 1
    bar_list([{"label": k, "value": v, "color": CHART_COLOR[k]} for k, v in counts.items()])
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(card_open("Attendance log"), unsafe_allow_html=True)
    if rows:
        display_rows = []
        for a in rows[:200]:
            e = get_employee(store, a["employeeId"])
            display_rows.append({"date": a["date"], "employeeCode": e["employeeCode"], "name": e["name"],
                                  "department": e["department"], "status": a["status"],
                                  "checkIn": a["checkIn"], "checkOut": a["checkOut"]})
        html_table(display_rows, [("date", "Date"), ("employeeCode", "Emp code"), ("name", "Name"),
                                   ("department", "Department"), ("status", "Status"),
                                   ("checkIn", "Check-in"), ("checkOut", "Check-out")],
                   badge_cols=("status",), mono_cols=("date", "checkIn", "checkOut"), code_cols=("employeeCode",))
        if len(rows) > 200:
            st.caption(f"Showing first 200 of {len(rows)} rows.")
    else:
        st.markdown('<div class="df-empty">No attendance records for this filter.</div>', unsafe_allow_html=True)
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    st.divider()
    with st.expander("✅ Manually mark / correct attendance (Admin override)"):
        with st.form("mark_att_form"):
            mc1, mc2, mc3 = st.columns(3)
            emp_options = {f'{e["name"]} ({e["employeeCode"]})': e["id"] for e in store["employees"]}
            emp_label = mc1.selectbox("Employee", list(emp_options.keys()))
            att_date = mc2.date_input("Date", value=datetime.now())
            att_status = mc3.selectbox("Status", ATTENDANCE_STATUSES)
            if st.form_submit_button("Save attendance", type="primary"):
                employee_id = emp_options[emp_label]
                date_str = att_date.strftime("%Y-%m-%d")
                existing = next((a for a in store["attendance"]
                                  if a["employeeId"] == employee_id and a["date"] == date_str), None)
                if existing:
                    existing["status"] = att_status
                else:
                    next_id = max([a["id"] for a in store["attendance"]], default=0) + 1
                    store["attendance"].append({"id": next_id, "employeeId": employee_id, "date": date_str,
                                                 "status": att_status, "checkIn": None, "checkOut": None})
                commit()
                st.success("Attendance saved.")
                st.rerun()


# ============================================================
# PAGE: Leave Approvals
# ============================================================

def render_leave():
    page_header("Leave Approvals", "Review, approve, or reject employee time-off requests.")

    pending = [l for l in store["leaveRequests"] if l["status"] == "Pending"]
    metric_grid([("Pending requests", len(pending))])

    tab_pending, tab_all = st.tabs([f"Pending ({len(pending)})", "All requests"])

    with tab_pending:
        if not pending:
            st.markdown('<div class="df-empty">No pending leave requests. All caught up!</div>', unsafe_allow_html=True)
        for r in pending:
            e = get_employee(store, r["employeeId"])
            remarks_html = f'<div class="df-req-meta">Remarks: {esc(r["remarks"])}</div>' if r.get("remarks") else ""
            st.markdown(
                f'<div class="df-req-card"><div style="display:flex; justify-content:space-between; align-items:flex-start;">'
                f'<div><div class="df-req-name">{esc(e["name"])} · {esc(e["department"])} · '
                f'<span class="mono">{e["employeeCode"]}</span></div>'
                f'<div class="df-req-meta">{esc(r["leaveType"])} leave — <span class="mono">{r["startDate"]}</span> '
                f'to <span class="mono">{r["endDate"]}</span></div>{remarks_html}</div>{badge(r["status"])}</div></div>',
                unsafe_allow_html=True,
            )
            comment = st.text_input("Admin comment (optional)", key=f"comment_{r['id']}", label_visibility="collapsed",
                                     placeholder="Admin comment (optional)")
            bc1, bc2, _ = st.columns([1, 1, 4])
            if bc1.button("✓ Approve", key=f"approve_{r['id']}", type="primary"):
                r["status"] = "Approved"
                r["adminComment"] = comment
                commit()
                st.success(f"Approved {e['name']}'s request.")
                st.rerun()
            if bc2.button("✕ Reject", key=f"reject_{r['id']}"):
                r["status"] = "Rejected"
                r["adminComment"] = comment
                commit()
                st.warning(f"Rejected {e['name']}'s request.")
                st.rerun()
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    with tab_all:
        all_lv = sorted(store["leaveRequests"], key=lambda l: l["status"] != "Pending")
        rows = []
        for l in all_lv:
            e = get_employee(store, l["employeeId"])
            rows.append({"employeeCode": e["employeeCode"], "name": e["name"], "department": e["department"],
                         "leaveType": l["leaveType"], "startDate": l["startDate"], "endDate": l["endDate"],
                         "status": l["status"], "adminComment": l.get("adminComment", "")})
        st.markdown(card_open(), unsafe_allow_html=True)
        html_table(rows, [("employeeCode", "Emp code"), ("name", "Name"), ("department", "Department"),
                           ("leaveType", "Type"), ("startDate", "From"), ("endDate", "To"),
                           ("status", "Status"), ("adminComment", "Admin comment")],
                   badge_cols=("status",), mono_cols=("startDate", "endDate"), code_cols=("employeeCode",))
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)


# ============================================================
# PAGE: Payroll Management
# ============================================================

def render_payroll():
    page_header("Payroll Management", "View and update salary structures across the organization.")

    payroll = [{**e, "net": net_salary(e)} for e in store["employees"]]
    total = sum(e["net"] for e in payroll)
    avg = total / len(payroll) if payroll else 0
    highest = max((e["net"] for e in payroll), default=0)

    metric_grid([
        ("Total monthly payroll", f'<span class="mono">{fmt_money(total)}</span>'),
        ("Average salary", f'<span class="mono">{fmt_money(avg)}</span>'),
        ("Highest salary", f'<span class="mono">{fmt_money(highest)}</span>'),
    ])

    st.markdown(card_open("Salary table"), unsafe_allow_html=True)
    html_table(
        [{"employeeCode": e["employeeCode"], "name": e["name"], "department": e["department"],
          "basicSalary": fmt_money(e["basicSalary"]), "hra": fmt_money(e["hra"]),
          "allowances": fmt_money(e["allowances"]), "deductions": fmt_money(e["deductions"]),
          "net": fmt_money(e["net"])} for e in payroll],
        [("employeeCode", "Emp code"), ("name", "Name"), ("department", "Department"),
         ("basicSalary", "Basic"), ("hra", "HRA"), ("allowances", "Allowances"),
         ("deductions", "Deductions"), ("net", "Net salary")],
        code_cols=("employeeCode",), mono_cols=("basicSalary", "hra", "allowances", "deductions", "net"),
    )
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(card_open("Update salary structure"), unsafe_allow_html=True)
    emp_options = {f'{e["name"]} ({e["employeeCode"]})': e["id"] for e in store["employees"]}
    pay_label = st.selectbox("Select employee", list(emp_options.keys()), key="pay_select")
    pe = get_employee(store, emp_options[pay_label])

    with st.form("pay_form"):
        pc1, pc2, pc3, pc4 = st.columns(4)
        basic = pc1.number_input("Basic", min_value=0, step=500, value=pe["basicSalary"])
        hra = pc2.number_input("HRA", min_value=0, step=500, value=pe["hra"])
        allowances = pc3.number_input("Allowances", min_value=0, step=500, value=pe["allowances"])
        deductions = pc4.number_input("Deductions", min_value=0, step=500, value=pe["deductions"])
        if st.form_submit_button("Update payroll", type="primary"):
            pe["basicSalary"] = int(basic)
            pe["hra"] = int(hra)
            pe["allowances"] = int(allowances)
            pe["deductions"] = int(deductions)
            commit()
            st.success(f"Updated salary structure for {pe['name']}.")
            st.rerun()
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    st.markdown(card_open("Generate salary slip"), unsafe_allow_html=True)
    slip_label = st.selectbox("Employee for salary slip", list(emp_options.keys()), key="slip_select")
    if st.button("Generate slip"):
        se = get_employee(store, emp_options[slip_label])
        net = net_salary(se)
        month = datetime.now().strftime("%B %Y")
        text = f"""DAYFLOW HRMS — SALARY SLIP
---------------------------------
Employee   : {se['name']} ({se['employeeCode']})
Department : {se['department']}
Designation: {se['designation']}
Month      : {month}
---------------------------------
Basic Salary   : {fmt_money(se['basicSalary'])}
HRA            : {fmt_money(se['hra'])}
Allowances     : {fmt_money(se['allowances'])}
Deductions     : {fmt_money(se['deductions'])}
---------------------------------
NET SALARY     : {fmt_money(net)}
---------------------------------
Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
        st.markdown(f'<div class="df-slip-box">{esc(text)}</div>', unsafe_allow_html=True)
        st.download_button("⬇ Download slip (.txt)", data=text, file_name=f"salary_slip_{se['employeeCode']}.txt")
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)


# ============================================================
# PAGE: Analytics & Reports
# ============================================================

def render_analytics():
    page_header("Analytics & Reports", "Organization-wide insights for HR decision-making.")

    tab_att, tab_lv, tab_pay = st.tabs(["Attendance analytics", "Leave analytics", "Payroll analytics"])
    att60 = attendance_in_range(store, 60)

    with tab_att:
        st.markdown(card_open("Attendance rate by department (last 60 days)"), unsafe_allow_html=True)
        by_dept: dict = {}
        for a in att60:
            e = get_employee(store, a["employeeId"])
            d = by_dept.setdefault(e["department"], {"total": 0, "present": 0})
            d["total"] += 1
            if a["status"] == "Present":
                d["present"] += 1
        bar_list([{"label": k, "value": round((v["present"] / v["total"]) * 100) if v["total"] else 0}
                   for k, v in by_dept.items()], max_value=100, value_fmt=lambda v: f"{v}%")
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

        st.markdown(card_open("Overall status breakdown (last 60 days)"), unsafe_allow_html=True)
        status_counts = {s: 0 for s in ATTENDANCE_STATUSES}
        for a in att60:
            status_counts[a["status"]] += 1
        bar_list([{"label": k, "value": v, "color": CHART_COLOR[k]} for k, v in status_counts.items()])
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    with tab_lv:
        st.markdown(card_open("Leave requests by type"), unsafe_allow_html=True)
        type_counts = {t: 0 for t in LEAVE_TYPES}
        for l in store["leaveRequests"]:
            type_counts[l["leaveType"]] += 1
        bar_list([{"label": k, "value": v} for k, v in type_counts.items()])
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

        st.markdown(card_open("Leave status breakdown"), unsafe_allow_html=True)
        lv_status_counts = {"Pending": 0, "Approved": 0, "Rejected": 0}
        for l in store["leaveRequests"]:
            lv_status_counts[l["status"]] += 1
        bar_list([{"label": k, "value": v, "color": CHART_COLOR[k]} for k, v in lv_status_counts.items()])
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    with tab_pay:
        st.markdown(card_open("Payroll by department"), unsafe_allow_html=True)
        dept_payroll: dict = {}
        for e in store["employees"]:
            dept_payroll[e["department"]] = dept_payroll.get(e["department"], 0) + net_salary(e)
        bar_list(sorted([{"label": k, "value": v, "color": GOLD} for k, v in dept_payroll.items()],
                         key=lambda d: -d["value"]), value_fmt=fmt_money)
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

        st.markdown(card_open("Salary distribution (top 10)"), unsafe_allow_html=True)
        salary_sorted = sorted(store["employees"], key=lambda e: -net_salary(e))[:10]
        bar_list([{"label": e["name"], "value": net_salary(e)} for e in salary_sorted], value_fmt=fmt_money)
        st.markdown(CARD_CLOSE, unsafe_allow_html=True)

    st.divider()
    st.markdown(card_open("Export reports"), unsafe_allow_html=True)
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        csv = to_csv_bytes(store["employees"], [
            ("employeeCode", "Employee Code"), ("name", "Name"), ("email", "Email"),
            ("department", "Department"), ("designation", "Designation"), ("role", "Role"),
            ("joinDate", "Join Date"), ("basicSalary", "Basic Salary"),
        ])
        st.download_button("⬇ Employee report (CSV)", data=csv, file_name="employee_report.csv")
    with ec2:
        rows = []
        for a in att60:
            e = get_employee(store, a["employeeId"])
            rows.append({**a, "name": e["name"], "department": e["department"]})
        csv = to_csv_bytes(rows, [
            ("date", "Date"), ("name", "Name"), ("department", "Department"),
            ("status", "Status"), ("checkIn", "Check-in"), ("checkOut", "Check-out"),
        ])
        st.download_button("⬇ Attendance report (CSV)", data=csv, file_name="attendance_report.csv")
    with ec3:
        rows = []
        for l in store["leaveRequests"]:
            e = get_employee(store, l["employeeId"])
            rows.append({**l, "name": e["name"], "department": e["department"]})
        csv = to_csv_bytes(rows, [
            ("name", "Name"), ("department", "Department"), ("leaveType", "Type"),
            ("startDate", "From"), ("endDate", "To"), ("status", "Status"), ("adminComment", "Admin Comment"),
        ])
        st.download_button("⬇ Leave report (CSV)", data=csv, file_name="leave_report.csv")
    st.markdown(CARD_CLOSE, unsafe_allow_html=True)


# ============================================================
# Router
# ============================================================

RENDERERS = {
    "dashboard": render_dashboard,
    "employees": render_employee_list,
    "employee-details": render_employee_details,
    "attendance": render_attendance,
    "leave": render_leave,
    "payroll": render_payroll,
    "analytics": render_analytics,
}

active_route = st.session_state.pop("route_override", None) or route
RENDERERS.get(active_route, render_dashboard)()
