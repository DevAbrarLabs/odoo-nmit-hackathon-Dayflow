/* ============================================================
   Dayflow HRMS — Admin Console
   Vanilla JS, hash-routed, localStorage-backed static site.
   Mirrors the Streamlit/Python reference app's 7 admin pages.
   ============================================================ */

let store = loadStore();

/* ---------------- Icons (inline, minimal) ---------------- */
const ICONS = {
  grid: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>`,
  users: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="8" r="3.2"/><path d="M2.5 20c0-3.5 3-6 6.5-6s6.5 2.5 6.5 6"/><circle cx="17.5" cy="8.5" r="2.4"/><path d="M15.5 14.2c2.8.4 5 2.6 5 5.8"/></svg>`,
  idcard: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2.5" y="5" width="19" height="14" rx="2"/><circle cx="8.5" cy="12" r="2.2"/><path d="M13.5 10.5h5M13.5 13.5h3.5M5 16.2h7"/></svg>`,
  clock: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>`,
  check: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12.5l5 5L20 6"/></svg>`,
  wallet: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2.5" y="6" width="19" height="13" rx="2"/><path d="M2.5 9.5H21"/><circle cx="16.5" cy="14" r="1.3" fill="currentColor" stroke="none"/></svg>`,
  chart: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 20V10M11 20V4M18 20v-7"/></svg>`,
};

const NAV = [
  { id: "dashboard", label: "Admin Dashboard", icon: ICONS.grid },
  { id: "employees", label: "Employee List", icon: ICONS.users },
  { id: "employee-details", label: "Employee Details", icon: ICONS.idcard },
  { id: "attendance", label: "Attendance Overview", icon: ICONS.clock },
  { id: "leave", label: "Leave Approvals", icon: ICONS.check },
  { id: "payroll", label: "Payroll Management", icon: ICONS.wallet },
  { id: "analytics", label: "Analytics & Reports", icon: ICONS.chart },
];

/* ---------------- Helpers ---------------- */

function fmtMoney(n) {
  return "₹" + Math.round(n).toLocaleString("en-IN");
}

function netSalary(e) {
  return e.basicSalary + e.hra + e.allowances - e.deductions;
}

function badge(status) {
  const map = {
    Present: "badge-present", Absent: "badge-absent", "Half-day": "badge-half", Leave: "badge-leave",
    Pending: "badge-pending", Approved: "badge-approved", Rejected: "badge-rejected",
  };
  return `<span class="badge ${map[status] || "badge-pending"}">${status}</span>`;
}

function initials(name) {
  return name.split(" ").map(p => p[0]).slice(0, 2).join("").toUpperCase();
}

function esc(str) {
  const d = document.createElement("div");
  d.textContent = str ?? "";
  return d.innerHTML;
}

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("show");
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove("show"), 2200);
}

function getEmployee(id) {
  return store.employees.find(e => e.id === Number(id));
}

function daysAgoISO(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

function attendanceInRange(days) {
  const since = daysAgoISO(days);
  return store.attendance.filter(a => a.date >= since);
}

function download(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

function toCSV(rows, columns) {
  const header = columns.map(c => c.label).join(",");
  const lines = rows.map(r => columns.map(c => {
    const v = r[c.key] ?? "";
    const s = String(v).replace(/"/g, '""');
    return /[,"\n]/.test(s) ? `"${s}"` : s;
  }).join(","));
  return [header, ...lines].join("\n");
}

/* ---------------- Signature element: the workday arc ----------------
   A thin arc tracing sunrise (9:00) to sunset (18:00), with a dot
   marking where the current moment falls in today's workday.
   This is the one recurring "brand" motif across every page. */

function workdayArcSVG() {
  const now = new Date();
  const startH = 9, endH = 18;
  const nowFrac = Math.min(1, Math.max(0, ((now.getHours() + now.getMinutes() / 60) - startH) / (endH - startH)));
  const w = 150, h = 26;
  const x0 = 6, x1 = w - 6;
  const midY = h - 6;
  const topY = 4;
  // quadratic arc control point
  const cx = (x0 + x1) / 2;
  const dotX = x0 + (x1 - x0) * nowFrac;
  // point on quadratic bezier: B(t) = (1-t)^2 P0 + 2(1-t)t C + t^2 P1
  const t = nowFrac;
  const dotY = (1 - t) * (1 - t) * midY + 2 * (1 - t) * t * topY + t * t * midY;
  const beforeSunset = now.getHours() < endH && now.getHours() >= startH;
  const label = beforeSunset ? `Workday · ${Math.round(nowFrac * 100)}% through` : (now.getHours() < startH ? "Before workday" : "Workday complete");

  return `
    <div class="flow-arc-wrap" title="${esc(label)}">
      <svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
        <path d="M${x0} ${midY} Q ${cx} ${topY} ${x1} ${midY}" fill="none" stroke="#E3E1D9" stroke-width="2" stroke-linecap="round"/>
        <path d="M${x0} ${midY} Q ${cx} ${topY} ${dotX} ${dotY}" fill="none" stroke="#E3A93C" stroke-width="2" stroke-linecap="round"/>
        <circle cx="${dotX}" cy="${dotY}" r="3.4" fill="#E3A93C"/>
      </svg>
      <span class="flow-arc-label">${esc(label)}</span>
    </div>`;
}

/* ---------------- Simple dependency-free bar chart ---------------- */

function barList(data, opts = {}) {
  // data: [{label, value}], opts: {max, colorClass, format}
  const max = opts.max || Math.max(1, ...data.map(d => d.value));
  const fmt = opts.format || (v => v);
  return `<div>${data.map(d => `
    <div class="bar-row">
      <div class="bar-label">${esc(d.label)}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.max(2, (d.value / max) * 100)}%; ${d.color ? `background:${d.color}` : ""}"></div></div>
      <div class="bar-value">${esc(String(fmt(d.value)))}</div>
    </div>`).join("")}</div>`;
}

/* ---------------- Router ---------------- */

function parseHash() {
  const raw = location.hash.replace(/^#\/?/, "");
  const [route, param] = raw.split("/");
  return { route: route || "dashboard", param };
}

function navigate(route, param) {
  location.hash = param ? `/${route}/${param}` : `/${route}`;
}

function renderNav(activeRoute) {
  const list = document.getElementById("nav-list");
  list.innerHTML = NAV.map(item => `
    <li>
      <button class="nav-item ${item.id === activeRoute ? "active" : ""}" data-nav="${item.id}">
        ${item.icon}<span>${item.label}</span>
      </button>
    </li>`).join("");
  list.querySelectorAll("[data-nav]").forEach(btn => {
    btn.addEventListener("click", () => navigate(btn.dataset.nav));
  });
}

function render() {
  const { route, param } = parseHash();
  renderNav(route);
  const main = document.getElementById("main-content");

  const renderers = {
    "dashboard": renderDashboard,
    "employees": renderEmployeeList,
    "employee-details": () => renderEmployeeDetails(param),
    "attendance": renderAttendance,
    "leave": renderLeave,
    "payroll": renderPayroll,
    "analytics": renderAnalytics,
  };

  const fn = renderers[route] || renderDashboard;
  main.innerHTML = fn.html ? fn.html() : fn();
  if (fn.after) fn.after();
}

window.addEventListener("hashchange", render);

document.getElementById("today-label").textContent =
  new Date().toLocaleDateString("en-US", { weekday: "long", day: "numeric", month: "long" });

/* ============================================================
   PAGE: Admin Dashboard
   ============================================================ */

function renderDashboard() {
  const emp = store.employees;
  const today = daysAgoISO(0);
  const todayAtt = store.attendance.filter(a => a.date === today);
  const pendingLeaves = store.leaveRequests.filter(l => l.status === "Pending");
  const presentToday = todayAtt.filter(a => a.status === "Present").length;
  const totalPayroll = emp.reduce((s, e) => s + netSalary(e), 0);

  const deptCounts = {};
  emp.forEach(e => deptCounts[e.department] = (deptCounts[e.department] || 0) + 1);
  const deptData = Object.entries(deptCounts).map(([label, value]) => ({ label, value })).sort((a, b) => b.value - a.value);

  const recentLeave = [...store.leaveRequests].sort((a, b) => (a.status === "Pending" ? -1 : 1)).slice(0, 5);

  const todayRows = todayAtt.map(a => {
    const e = getEmployee(a.employeeId);
    return `<tr>
      <td>${esc(e.name)}</td>
      <td>${esc(e.department)}</td>
      <td>${badge(a.status)}</td>
      <td class="mono">${a.checkIn || "—"}</td>
      <td class="mono">${a.checkOut || "—"}</td>
    </tr>`;
  }).join("");

  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Admin Dashboard</h1>
        <div class="page-sub">A snapshot of today across the organization.</div>
      </div>
      ${workdayArcSVG()}
    </div>

    <div class="grid grid-4 section">
      <div class="card metric-card">
        <div class="metric-label">Total Employees</div>
        <div class="metric-value">${emp.length}</div>
      </div>
      <div class="card metric-card">
        <div class="metric-label">Present Today</div>
        <div class="metric-value">${presentToday}</div>
      </div>
      <div class="card metric-card">
        <div class="metric-label">Pending Leave Requests</div>
        <div class="metric-value">${pendingLeaves.length}</div>
      </div>
      <div class="card metric-card">
        <div class="metric-label">Monthly Payroll (est.)</div>
        <div class="metric-value mono">${fmtMoney(totalPayroll)}</div>
      </div>
    </div>

    <div class="grid grid-2 section">
      <div class="card">
        <div class="card-title">Department Distribution</div>
        ${barList(deptData, { color: "#E3A93C" })}
      </div>
      <div class="card">
        <div class="card-title">Recent Leave Requests</div>
        ${recentLeave.length ? recentLeave.map(r => {
          const e = getEmployee(r.employeeId);
          return `<div style="margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <strong style="font-size:13.5px;">${esc(e.name)}</strong>
              ${badge(r.status)}
            </div>
            <div class="req-meta">${esc(e.department)} · ${esc(r.leaveType)} leave</div>
            <div class="req-meta mono">${r.startDate} → ${r.endDate}</div>
          </div>`;
        }).join("") : `<div class="empty-state">No leave requests yet.</div>`}
      </div>
    </div>

    <div class="card section">
      <div class="card-title">Today's Attendance Snapshot</div>
      ${todayAtt.length ? `<div class="table-wrap"><table>
        <thead><tr><th>Name</th><th>Department</th><th>Status</th><th>Check-in</th><th>Check-out</th></tr></thead>
        <tbody>${todayRows}</tbody>
      </table></div>` : `<div class="empty-state">No attendance logged yet for today.</div>`}
    </div>
  `;
}

/* ============================================================
   PAGE: Employee List
   ============================================================ */

let empListFilters = { search: "", dept: "All", role: "All" };

function renderEmployeeList() {
  const depts = ["All", ...new Set(store.employees.map(e => e.department))].sort((a, b) => a === "All" ? -1 : a.localeCompare(b));

  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Employee List</h1>
        <div class="page-sub">Browse, search, and manage every employee in the organization.</div>
      </div>
      ${workdayArcSVG()}
    </div>

    <div class="toolbar">
      <div class="field grow">
        <label>Search</label>
        <input type="text" id="el-search" placeholder="Search by name, email, or employee code" value="${esc(empListFilters.search)}">
      </div>
      <div class="field">
        <label>Department</label>
        <select id="el-dept">${depts.map(d => `<option ${d === empListFilters.dept ? "selected" : ""}>${esc(d)}</option>`).join("")}</select>
      </div>
      <div class="field">
        <label>Role</label>
        <select id="el-role">
          ${["All", "Employee", "Admin"].map(r => `<option ${r === empListFilters.role ? "selected" : ""}>${r}</option>`).join("")}
        </select>
      </div>
    </div>

    <div id="el-table-mount"></div>

    <div class="divider"></div>

    <details class="inline-form">
      <summary>➕ Add new employee</summary>
      <form id="add-emp-form">
        <div class="form-grid">
          <div class="field"><label>Full name</label><input type="text" name="name" required></div>
          <div class="field"><label>Email</label><input type="email" name="email" required></div>
          <div class="field">
            <label>Department</label>
            <select name="department" id="add-emp-dept">${DEPARTMENTS.map(d => `<option>${d}</option>`).join("")}</select>
          </div>
          <div class="field">
            <label>Designation</label>
            <select name="designation" id="add-emp-designation">${DESIGNATIONS[DEPARTMENTS[0]].map(d => `<option>${d}</option>`).join("")}</select>
          </div>
          <div class="field"><label>Basic salary (₹)</label><input type="number" name="basicSalary" value="30000" min="0" step="1000"></div>
          <div class="field">
            <label>Role</label>
            <select name="role"><option>Employee</option><option>Admin</option></select>
          </div>
          <div class="field" style="justify-content:flex-end;">
            <button type="submit" class="btn btn-primary">Add employee</button>
          </div>
        </div>
      </form>
    </details>
  `;
}
renderEmployeeList.after = function () {
  const searchEl = document.getElementById("el-search");
  const deptEl = document.getElementById("el-dept");
  const roleEl = document.getElementById("el-role");

  function drawTable() {
    let rows = store.employees;
    const s = empListFilters.search.toLowerCase();
    if (s) rows = rows.filter(e => e.name.toLowerCase().includes(s) || e.email.toLowerCase().includes(s) || e.employeeCode.toLowerCase().includes(s));
    if (empListFilters.dept !== "All") rows = rows.filter(e => e.department === empListFilters.dept);
    if (empListFilters.role !== "All") rows = rows.filter(e => e.role === empListFilters.role);

    const mount = document.getElementById("el-table-mount");
    mount.innerHTML = `
      <div class="page-sub" style="margin-bottom:10px;">Showing <strong>${rows.length}</strong> of <strong>${store.employees.length}</strong> employees</div>
      <div class="card table-wrap">
        <table>
          <thead><tr><th>Emp code</th><th>Name</th><th>Email</th><th>Department</th><th>Designation</th><th>Role</th><th>Joined</th></tr></thead>
          <tbody>
            ${rows.length ? rows.map(e => `
              <tr class="emp-row" data-id="${e.id}" style="cursor:pointer;">
                <td class="emp-code">${esc(e.employeeCode)}</td>
                <td>${esc(e.name)}</td>
                <td>${esc(e.email)}</td>
                <td>${esc(e.department)}</td>
                <td>${esc(e.designation)}</td>
                <td>${esc(e.role)}</td>
                <td class="mono">${e.joinDate}</td>
              </tr>`).join("") : `<tr><td colspan="7"><div class="empty-state">No employees match these filters.</div></td></tr>`}
          </tbody>
        </table>
      </div>`;
    mount.querySelectorAll(".emp-row").forEach(tr => {
      tr.addEventListener("click", () => navigate("employee-details", tr.dataset.id));
    });
  }

  searchEl.addEventListener("input", () => { empListFilters.search = searchEl.value; drawTable(); });
  deptEl.addEventListener("change", () => { empListFilters.dept = deptEl.value; drawTable(); });
  roleEl.addEventListener("change", () => { empListFilters.role = roleEl.value; drawTable(); });
  drawTable();

  const addDeptEl = document.getElementById("add-emp-dept");
  const addDesigEl = document.getElementById("add-emp-designation");
  addDeptEl.addEventListener("change", () => {
    addDesigEl.innerHTML = DESIGNATIONS[addDeptEl.value].map(d => `<option>${d}</option>`).join("");
  });

  document.getElementById("add-emp-form").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const f = new FormData(ev.target);
    const email = f.get("email").trim();
    if (store.employees.some(e => e.email.toLowerCase() === email.toLowerCase())) {
      toast("An employee with that email already exists.");
      return;
    }
    const basic = Number(f.get("basicSalary")) || 0;
    const nextId = Math.max(...store.employees.map(e => e.id)) + 1;
    store.employees.push({
      id: nextId,
      employeeCode: `DF${1000 + nextId}`,
      name: f.get("name").trim(),
      email,
      role: f.get("role"),
      department: f.get("department"),
      designation: f.get("designation"),
      phone: "", address: "",
      joinDate: new Date().toISOString().slice(0, 10),
      basicSalary: basic,
      hra: Math.round(basic * 0.4),
      allowances: Math.round(basic * 0.15),
      deductions: Math.round(basic * 0.08),
    });
    saveStore(store);
    toast(`Added ${f.get("name").trim()}.`);
    ev.target.reset();
    drawTable();
  });
};

/* ============================================================
   PAGE: Employee Details
   ============================================================ */

function renderEmployeeDetails(paramId) {
  const emp = store.employees;
  if (!emp.length) return `<div class="empty-state">No employees yet.</div>`;
  const selectedId = paramId ? Number(paramId) : emp[0].id;
  const e = getEmployee(selectedId) || emp[0];

  const att = store.attendance.filter(a => a.employeeId === e.id).sort((a, b) => b.date.localeCompare(a.date)).slice(0, 14);
  const lv = store.leaveRequests.filter(l => l.employeeId === e.id).sort((a, b) => b.startDate.localeCompare(a.startDate));

  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Employee Details</h1>
        <div class="page-sub">Full profile, salary structure, and history for one employee.</div>
      </div>
      ${workdayArcSVG()}
    </div>

    <div class="field" style="max-width:340px; margin-bottom:20px;">
      <label>Select an employee</label>
      <select id="ed-select" class="select-emp">
        ${emp.map(x => `<option value="${x.id}" ${x.id === e.id ? "selected" : ""}>${esc(x.name)} (${x.employeeCode})</option>`).join("")}
      </select>
    </div>

    <div class="two-col">
      <div class="card">
        <div class="profile-head">
          <div class="avatar-circle">${initials(e.name)}</div>
          <div>
            <h3>${esc(e.name)}</h3>
            <div class="page-sub" style="margin-top:2px;">${esc(e.designation)} · ${esc(e.department)}</div>
          </div>
        </div>
        <div class="divider"></div>
        <div style="font-size:13.5px; line-height:2;">
          <div><span class="metric-label" style="display:inline;">Emp code&nbsp;</span> <span class="mono">${esc(e.employeeCode)}</span></div>
          <div><span class="metric-label" style="display:inline;">Role&nbsp;</span> ${esc(e.role)}</div>
          <div><span class="metric-label" style="display:inline;">Joined&nbsp;</span> <span class="mono">${e.joinDate}</span></div>
        </div>
      </div>

      <div class="card">
        <div class="tabs">
          <button class="tab-btn active" data-tab="profile">Profile</button>
          <button class="tab-btn" data-tab="salary">Salary structure</button>
          <button class="tab-btn" data-tab="history">Attendance &amp; leave</button>
        </div>

        <div class="tab-panel active" data-panel="profile">
          <form id="edit-profile-form">
            <div class="form-grid" style="grid-template-columns:1fr 1fr;">
              <div class="field"><label>Email</label><input type="email" name="email" value="${esc(e.email)}"></div>
              <div class="field"><label>Phone</label><input type="text" name="phone" value="${esc(e.phone || "")}"></div>
            </div>
            <div class="field" style="margin-top:12px;"><label>Address</label><textarea name="address">${esc(e.address || "")}</textarea></div>
            <div class="form-grid" style="grid-template-columns:1fr 1fr; margin-top:12px;">
              <div class="field">
                <label>Department</label>
                <select name="department" id="ed-dept">${DEPARTMENTS.map(d => `<option ${d === e.department ? "selected" : ""}>${d}</option>`).join("")}</select>
              </div>
              <div class="field">
                <label>Designation</label>
                <select name="designation" id="ed-designation">${DESIGNATIONS[e.department].map(d => `<option ${d === e.designation ? "selected" : ""}>${d}</option>`).join("")}</select>
              </div>
            </div>
            <button type="submit" class="btn btn-primary" style="margin-top:16px;">Save changes (Admin)</button>
          </form>
        </div>

        <div class="tab-panel" data-panel="salary">
          <div class="metric-label">Net monthly salary</div>
          <div class="metric-value mono" style="margin-bottom:16px;">${fmtMoney(netSalary(e))}</div>
          <div class="grid grid-4">
            <div class="card metric-card"><div class="metric-label">Basic</div><div class="metric-value mono" style="font-size:18px;">${fmtMoney(e.basicSalary)}</div></div>
            <div class="card metric-card"><div class="metric-label">HRA</div><div class="metric-value mono" style="font-size:18px;">${fmtMoney(e.hra)}</div></div>
            <div class="card metric-card"><div class="metric-label">Allowances</div><div class="metric-value mono" style="font-size:18px;">${fmtMoney(e.allowances)}</div></div>
            <div class="card metric-card"><div class="metric-label">Deductions</div><div class="metric-value mono" style="font-size:18px;">${fmtMoney(e.deductions)}</div></div>
          </div>
        </div>

        <div class="tab-panel" data-panel="history">
          <div class="card-title">Last 14 attendance entries</div>
          ${att.length ? `<div class="table-wrap"><table>
            <thead><tr><th>Date</th><th>Status</th><th>Check-in</th><th>Check-out</th></tr></thead>
            <tbody>${att.map(a => `<tr><td class="mono">${a.date}</td><td>${badge(a.status)}</td><td class="mono">${a.checkIn || "—"}</td><td class="mono">${a.checkOut || "—"}</td></tr>`).join("")}</tbody>
          </table></div>` : `<div class="empty-state">No attendance records.</div>`}
          <div class="divider"></div>
          <div class="card-title">Leave history</div>
          ${lv.length ? `<div class="table-wrap"><table>
            <thead><tr><th>Type</th><th>From</th><th>To</th><th>Status</th><th>Remarks</th></tr></thead>
            <tbody>${lv.map(l => `<tr><td>${esc(l.leaveType)}</td><td class="mono">${l.startDate}</td><td class="mono">${l.endDate}</td><td>${badge(l.status)}</td><td>${esc(l.remarks)}</td></tr>`).join("")}</tbody>
          </table></div>` : `<div class="empty-state">No leave requests.</div>`}
        </div>
      </div>
    </div>
  `;
}
renderEmployeeDetails.after = function () {
  const select = document.getElementById("ed-select");
  if (select) select.addEventListener("change", () => navigate("employee-details", select.value));

  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.querySelector(`.tab-panel[data-panel="${btn.dataset.tab}"]`).classList.add("active");
    });
  });

  const deptEl = document.getElementById("ed-dept");
  const desigEl = document.getElementById("ed-designation");
  if (deptEl) deptEl.addEventListener("change", () => {
    desigEl.innerHTML = DESIGNATIONS[deptEl.value].map(d => `<option>${d}</option>`).join("");
  });

  const form = document.getElementById("edit-profile-form");
  if (form) form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const { route, param } = parseHash();
    const e = getEmployee(param);
    const f = new FormData(ev.target);
    e.email = f.get("email"); e.phone = f.get("phone"); e.address = f.get("address");
    e.department = f.get("department"); e.designation = f.get("designation");
    saveStore(store);
    toast("Profile updated.");
  });
};

/* ============================================================
   PAGE: Attendance Overview
   ============================================================ */

let attFilters = { days: 14, dept: "All", status: "All" };

function renderAttendance() {
  const depts = ["All", ...new Set(store.employees.map(e => e.department))];
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Attendance Overview</h1>
        <div class="page-sub">Company-wide attendance across all employees.</div>
      </div>
      ${workdayArcSVG()}
    </div>

    <div class="toolbar">
      <div class="field">
        <label>Show last N days: <span id="att-days-val">${attFilters.days}</span></label>
        <input type="range" id="att-days" min="1" max="45" value="${attFilters.days}">
      </div>
      <div class="field">
        <label>Department</label>
        <select id="att-dept">${depts.map(d => `<option ${d === attFilters.dept ? "selected" : ""}>${d}</option>`).join("")}</select>
      </div>
      <div class="field">
        <label>Status</label>
        <select id="att-status">${["All", ...ATTENDANCE_STATUSES].map(s => `<option ${s === attFilters.status ? "selected" : ""}>${s}</option>`).join("")}</select>
      </div>
    </div>

    <div class="card section">
      <div class="card-title">Status breakdown (filtered range)</div>
      <div id="att-chart-mount"></div>
    </div>

    <div class="card">
      <div class="card-title">Attendance log</div>
      <div id="att-table-mount"></div>
    </div>

    <div class="divider"></div>

    <details class="inline-form">
      <summary>✅ Manually mark / correct attendance (Admin override)</summary>
      <form id="mark-att-form">
        <div class="form-grid">
          <div class="field">
            <label>Employee</label>
            <select name="employeeId">${store.employees.map(e => `<option value="${e.id}">${esc(e.name)} (${e.employeeCode})</option>`).join("")}</select>
          </div>
          <div class="field"><label>Date</label><input type="date" name="date" value="${daysAgoISO(0)}"></div>
          <div class="field">
            <label>Status</label>
            <select name="status">${ATTENDANCE_STATUSES.map(s => `<option>${s}</option>`).join("")}</select>
          </div>
          <div class="field" style="justify-content:flex-end;"><button type="submit" class="btn btn-primary">Save attendance</button></div>
        </div>
      </form>
    </details>
  `;
}
renderAttendance.after = function () {
  function draw() {
    const rows = attendanceInRange(attFilters.days).filter(a => {
      const e = getEmployee(a.employeeId);
      if (attFilters.dept !== "All" && e.department !== attFilters.dept) return false;
      if (attFilters.status !== "All" && a.status !== attFilters.status) return false;
      return true;
    }).sort((a, b) => b.date.localeCompare(a.date));

    const counts = {};
    ATTENDANCE_STATUSES.forEach(s => counts[s] = 0);
    rows.forEach(a => counts[a.status]++);
    const colorMap = { Present: "#2F8558", Absent: "#C13F3F", "Half-day": "#E3A93C", Leave: "#3B5EA8" };
    document.getElementById("att-chart-mount").innerHTML = barList(
      Object.entries(counts).map(([label, value]) => ({ label, value, color: colorMap[label] })),
    );

    document.getElementById("att-table-mount").innerHTML = rows.length ? `
      <div class="table-wrap"><table>
        <thead><tr><th>Date</th><th>Emp code</th><th>Name</th><th>Department</th><th>Status</th><th>Check-in</th><th>Check-out</th></tr></thead>
        <tbody>${rows.slice(0, 200).map(a => {
          const e = getEmployee(a.employeeId);
          return `<tr><td class="mono">${a.date}</td><td class="emp-code">${e.employeeCode}</td><td>${esc(e.name)}</td><td>${esc(e.department)}</td><td>${badge(a.status)}</td><td class="mono">${a.checkIn || "—"}</td><td class="mono">${a.checkOut || "—"}</td></tr>`;
        }).join("")}</tbody>
      </table></div>
      ${rows.length > 200 ? `<div class="page-sub" style="margin-top:8px;">Showing first 200 of ${rows.length} rows.</div>` : ""}
    ` : `<div class="empty-state">No attendance records for this filter.</div>`;
  }

  const daysEl = document.getElementById("att-days");
  daysEl.addEventListener("input", () => {
    attFilters.days = Number(daysEl.value);
    document.getElementById("att-days-val").textContent = attFilters.days;
    draw();
  });
  document.getElementById("att-dept").addEventListener("change", (e) => { attFilters.dept = e.target.value; draw(); });
  document.getElementById("att-status").addEventListener("change", (e) => { attFilters.status = e.target.value; draw(); });
  draw();

  document.getElementById("mark-att-form").addEventListener("submit", (ev) => {
    ev.preventDefault();
    const f = new FormData(ev.target);
    const employeeId = Number(f.get("employeeId"));
    const date = f.get("date");
    const status = f.get("status");
    const existing = store.attendance.find(a => a.employeeId === employeeId && a.date === date);
    if (existing) existing.status = status;
    else store.attendance.push({ id: Math.max(0, ...store.attendance.map(a => a.id)) + 1, employeeId, date, status, checkIn: null, checkOut: null });
    saveStore(store);
    toast("Attendance saved.");
    draw();
  });
};

/* ============================================================
   PAGE: Leave Approvals
   ============================================================ */

function renderLeave() {
  const pending = store.leaveRequests.filter(l => l.status === "Pending");
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Leave Approvals</h1>
        <div class="page-sub">Review, approve, or reject employee time-off requests.</div>
      </div>
      ${workdayArcSVG()}
    </div>

    <div class="grid grid-4 section" style="grid-template-columns: 220px;">
      <div class="card metric-card">
        <div class="metric-label">Pending requests</div>
        <div class="metric-value">${pending.length}</div>
      </div>
    </div>

    <div class="tabs">
      <button class="tab-btn active" data-tab="pending">Pending (${pending.length})</button>
      <button class="tab-btn" data-tab="all">All requests</button>
    </div>

    <div class="tab-panel active" data-panel="pending" id="lv-pending-mount"></div>
    <div class="tab-panel" data-panel="all" id="lv-all-mount"></div>
  `;
}
renderLeave.after = function () {
  function drawPending() {
    const pending = store.leaveRequests.filter(l => l.status === "Pending");
    const mount = document.getElementById("lv-pending-mount");
    if (!pending.length) { mount.innerHTML = `<div class="empty-state">No pending leave requests. All caught up!</div>`; return; }
    mount.innerHTML = pending.map(r => {
      const e = getEmployee(r.employeeId);
      return `
      <div class="req-card">
        <div class="req-card-top">
          <div>
            <div class="req-name">${esc(e.name)} · ${esc(e.department)} · <span class="mono">${e.employeeCode}</span></div>
            <div class="req-meta">${esc(r.leaveType)} leave — <span class="mono">${r.startDate}</span> to <span class="mono">${r.endDate}</span></div>
            ${r.remarks ? `<div class="req-meta">Remarks: ${esc(r.remarks)}</div>` : ""}
          </div>
          ${badge(r.status)}
        </div>
        <div class="field"><input type="text" placeholder="Admin comment (optional)" data-comment="${r.id}"></div>
        <div class="req-actions">
          <button class="btn btn-primary btn-sm" data-approve="${r.id}">✓ Approve</button>
          <button class="btn btn-danger btn-sm" data-reject="${r.id}">✕ Reject</button>
        </div>
      </div>`;
    }).join("");

    mount.querySelectorAll("[data-approve]").forEach(btn => btn.addEventListener("click", () => {
      const id = Number(btn.dataset.approve);
      const comment = mount.querySelector(`[data-comment="${id}"]`).value;
      const r = store.leaveRequests.find(x => x.id === id);
      r.status = "Approved"; r.adminComment = comment;
      saveStore(store);
      toast(`Approved ${getEmployee(r.employeeId).name}'s request.`);
      drawPending(); drawAll();
      updateTabCounts();
    }));
    mount.querySelectorAll("[data-reject]").forEach(btn => btn.addEventListener("click", () => {
      const id = Number(btn.dataset.reject);
      const comment = mount.querySelector(`[data-comment="${id}"]`).value;
      const r = store.leaveRequests.find(x => x.id === id);
      r.status = "Rejected"; r.adminComment = comment;
      saveStore(store);
      toast(`Rejected ${getEmployee(r.employeeId).name}'s request.`);
      drawPending(); drawAll();
      updateTabCounts();
    }));
  }

  function drawAll() {
    const all = [...store.leaveRequests].sort((a, b) => (a.status === "Pending" ? -1 : 1));
    document.getElementById("lv-all-mount").innerHTML = all.length ? `
      <div class="card table-wrap"><table>
        <thead><tr><th>Emp code</th><th>Name</th><th>Department</th><th>Type</th><th>From</th><th>To</th><th>Status</th><th>Admin comment</th></tr></thead>
        <tbody>${all.map(l => {
          const e = getEmployee(l.employeeId);
          return `<tr><td class="emp-code">${e.employeeCode}</td><td>${esc(e.name)}</td><td>${esc(e.department)}</td><td>${esc(l.leaveType)}</td><td class="mono">${l.startDate}</td><td class="mono">${l.endDate}</td><td>${badge(l.status)}</td><td>${esc(l.adminComment || "")}</td></tr>`;
        }).join("")}</tbody>
      </table></div>` : `<div class="empty-state">No leave requests yet.</div>`;
  }

  function updateTabCounts() {
    const pending = store.leaveRequests.filter(l => l.status === "Pending");
    document.querySelector('[data-tab="pending"]').textContent = `Pending (${pending.length})`;
  }

  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.querySelector(`.tab-panel[data-panel="${btn.dataset.tab}"]`).classList.add("active");
    });
  });

  drawPending();
  drawAll();
};

/* ============================================================
   PAGE: Payroll Management
   ============================================================ */

function renderPayroll() {
  const payroll = store.employees.map(e => ({ ...e, net: netSalary(e) }));
  const total = payroll.reduce((s, e) => s + e.net, 0);
  const avg = total / (payroll.length || 1);
  const max = Math.max(...payroll.map(e => e.net));

  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Payroll Management</h1>
        <div class="page-sub">View and update salary structures across the organization.</div>
      </div>
      ${workdayArcSVG()}
    </div>

    <div class="grid grid-3 section">
      <div class="card metric-card"><div class="metric-label">Total monthly payroll</div><div class="metric-value mono">${fmtMoney(total)}</div></div>
      <div class="card metric-card"><div class="metric-label">Average salary</div><div class="metric-value mono">${fmtMoney(avg)}</div></div>
      <div class="card metric-card"><div class="metric-label">Highest salary</div><div class="metric-value mono">${fmtMoney(max)}</div></div>
    </div>

    <div class="card section table-wrap">
      <div class="card-title">Salary table</div>
      <table>
        <thead><tr><th>Emp code</th><th>Name</th><th>Department</th><th>Basic</th><th>HRA</th><th>Allowances</th><th>Deductions</th><th>Net salary</th></tr></thead>
        <tbody>${payroll.map(e => `<tr>
          <td class="emp-code">${e.employeeCode}</td><td>${esc(e.name)}</td><td>${esc(e.department)}</td>
          <td class="money">${fmtMoney(e.basicSalary)}</td><td class="money">${fmtMoney(e.hra)}</td>
          <td class="money">${fmtMoney(e.allowances)}</td><td class="money">${fmtMoney(e.deductions)}</td>
          <td class="money"><strong>${fmtMoney(e.net)}</strong></td>
        </tr>`).join("")}</tbody>
      </table>
    </div>

    <div class="card section">
      <div class="card-title">Update salary structure</div>
      <div class="field" style="max-width:340px; margin-bottom:16px;">
        <label>Select employee</label>
        <select id="pay-select" class="select-emp">${store.employees.map(e => `<option value="${e.id}">${esc(e.name)} (${e.employeeCode})</option>`).join("")}</select>
      </div>
      <form id="pay-form">
        <div class="form-grid">
          <div class="field"><label>Basic</label><input type="number" name="basicSalary" min="0" step="500"></div>
          <div class="field"><label>HRA</label><input type="number" name="hra" min="0" step="500"></div>
          <div class="field"><label>Allowances</label><input type="number" name="allowances" min="0" step="500"></div>
          <div class="field"><label>Deductions</label><input type="number" name="deductions" min="0" step="500"></div>
        </div>
        <button type="submit" class="btn btn-primary" style="margin-top:14px;">Update payroll</button>
      </form>
    </div>

    <div class="card">
      <div class="card-title">Generate salary slip</div>
      <div class="field" style="max-width:340px; margin-bottom:16px;">
        <label>Employee for salary slip</label>
        <select id="slip-select" class="select-emp">${store.employees.map(e => `<option value="${e.id}">${esc(e.name)} (${e.employeeCode})</option>`).join("")}</select>
      </div>
      <button class="btn btn-gold" id="slip-generate">Generate slip</button>
      <div id="slip-mount" style="margin-top:16px;"></div>
    </div>
  `;
}
renderPayroll.after = function () {
  const payForm = document.getElementById("pay-form");
  const paySelect = document.getElementById("pay-select");

  function fillPayForm() {
    const e = getEmployee(paySelect.value);
    payForm.basicSalary.value = e.basicSalary;
    payForm.hra.value = e.hra;
    payForm.allowances.value = e.allowances;
    payForm.deductions.value = e.deductions;
  }
  paySelect.addEventListener("change", fillPayForm);
  fillPayForm();

  payForm.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const e = getEmployee(paySelect.value);
    e.basicSalary = Number(payForm.basicSalary.value) || 0;
    e.hra = Number(payForm.hra.value) || 0;
    e.allowances = Number(payForm.allowances.value) || 0;
    e.deductions = Number(payForm.deductions.value) || 0;
    saveStore(store);
    toast(`Updated salary structure for ${e.name}.`);
  });

  document.getElementById("slip-generate").addEventListener("click", () => {
    const e = getEmployee(document.getElementById("slip-select").value);
    const net = netSalary(e);
    const month = new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" });
    const text = `DAYFLOW HRMS — SALARY SLIP
---------------------------------
Employee   : ${e.name} (${e.employeeCode})
Department : ${e.department}
Designation: ${e.designation}
Month      : ${month}
---------------------------------
Basic Salary   : ${fmtMoney(e.basicSalary)}
HRA            : ${fmtMoney(e.hra)}
Allowances     : ${fmtMoney(e.allowances)}
Deductions     : ${fmtMoney(e.deductions)}
---------------------------------
NET SALARY     : ${fmtMoney(net)}
---------------------------------
Generated on ${new Date().toLocaleString()}`;
    document.getElementById("slip-mount").innerHTML = `
      <div class="slip-box">${esc(text)}</div>
      <button class="btn btn-primary" id="slip-download" style="margin-top:12px;">⬇ Download slip (.txt)</button>
    `;
    document.getElementById("slip-download").addEventListener("click", () => download(`salary_slip_${e.employeeCode}.txt`, text));
  });
};

/* ============================================================
   PAGE: Analytics & Reports
   ============================================================ */

function renderAnalytics() {
  return `
    <div class="page-header">
      <div>
        <h1 class="page-title">Analytics &amp; Reports</h1>
        <div class="page-sub">Organization-wide insights for HR decision-making.</div>
      </div>
      ${workdayArcSVG()}
    </div>

    <div class="tabs">
      <button class="tab-btn active" data-tab="att">Attendance analytics</button>
      <button class="tab-btn" data-tab="lv">Leave analytics</button>
      <button class="tab-btn" data-tab="pay">Payroll analytics</button>
    </div>

    <div class="tab-panel active" data-panel="att">
      <div class="card section">
        <div class="card-title">Attendance rate by department (last 60 days)</div>
        <div id="an-dept-att-mount"></div>
      </div>
      <div class="card">
        <div class="card-title">Overall status breakdown (last 60 days)</div>
        <div id="an-status-mount"></div>
      </div>
    </div>

    <div class="tab-panel" data-panel="lv">
      <div class="card section">
        <div class="card-title">Leave requests by type</div>
        <div id="an-leave-type-mount"></div>
      </div>
      <div class="card">
        <div class="card-title">Leave status breakdown</div>
        <div id="an-leave-status-mount"></div>
      </div>
    </div>

    <div class="tab-panel" data-panel="pay">
      <div class="card section">
        <div class="card-title">Payroll by department</div>
        <div id="an-payroll-dept-mount"></div>
      </div>
      <div class="card">
        <div class="card-title">Salary distribution</div>
        <div id="an-salary-dist-mount"></div>
      </div>
    </div>

    <div class="divider"></div>
    <div class="card">
      <div class="card-title">Export reports</div>
      <div style="display:flex; gap:10px; flex-wrap:wrap;">
        <button class="btn btn-primary btn-sm" id="exp-employees">⬇ Employee report (CSV)</button>
        <button class="btn btn-primary btn-sm" id="exp-attendance">⬇ Attendance report (CSV)</button>
        <button class="btn btn-primary btn-sm" id="exp-leave">⬇ Leave report (CSV)</button>
      </div>
    </div>
  `;
}
renderAnalytics.after = function () {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.querySelector(`.tab-panel[data-panel="${btn.dataset.tab}"]`).classList.add("active");
    });
  });

  const att60 = attendanceInRange(60);

  // Attendance rate by department
  const byDept = {};
  att60.forEach(a => {
    const e = getEmployee(a.employeeId);
    byDept[e.department] = byDept[e.department] || { total: 0, present: 0 };
    byDept[e.department].total++;
    if (a.status === "Present") byDept[e.department].present++;
  });
  document.getElementById("an-dept-att-mount").innerHTML = barList(
    Object.entries(byDept).map(([label, v]) => ({ label, value: Math.round((v.present / v.total) * 100) })),
    { max: 100, format: v => v + "%" }
  );

  // Overall status breakdown
  const statusCounts = {};
  ATTENDANCE_STATUSES.forEach(s => statusCounts[s] = 0);
  att60.forEach(a => statusCounts[a.status]++);
  const colorMap = { Present: "#2F8558", Absent: "#C13F3F", "Half-day": "#E3A93C", Leave: "#3B5EA8" };
  document.getElementById("an-status-mount").innerHTML = barList(
    Object.entries(statusCounts).map(([label, value]) => ({ label, value, color: colorMap[label] }))
  );

  // Leave by type
  const typeCounts = {};
  LEAVE_TYPES.forEach(t => typeCounts[t] = 0);
  store.leaveRequests.forEach(l => typeCounts[l.leaveType]++);
  document.getElementById("an-leave-type-mount").innerHTML = barList(
    Object.entries(typeCounts).map(([label, value]) => ({ label, value }))
  );

  // Leave status breakdown
  const lvStatusCounts = { Pending: 0, Approved: 0, Rejected: 0 };
  store.leaveRequests.forEach(l => lvStatusCounts[l.status]++);
  document.getElementById("an-leave-status-mount").innerHTML = barList(
    Object.entries(lvStatusCounts).map(([label, value]) => ({ label, value, color: colorMap[label === "Approved" ? "Present" : label === "Rejected" ? "Absent" : "Leave"] }))
  );

  // Payroll by department
  const deptPayroll = {};
  store.employees.forEach(e => { deptPayroll[e.department] = (deptPayroll[e.department] || 0) + netSalary(e); });
  document.getElementById("an-payroll-dept-mount").innerHTML = barList(
    Object.entries(deptPayroll).sort((a, b) => b[1] - a[1]).map(([label, value]) => ({ label, value, color: "#E3A93C" })),
    { format: fmtMoney }
  );

  // Salary distribution (top 10 by salary, to keep the list readable)
  const salarySorted = [...store.employees].sort((a, b) => netSalary(b) - netSalary(a)).slice(0, 10);
  document.getElementById("an-salary-dist-mount").innerHTML = barList(
    salarySorted.map(e => ({ label: e.name, value: netSalary(e) })),
    { format: fmtMoney }
  );

  document.getElementById("exp-employees").addEventListener("click", () => {
    const csv = toCSV(store.employees, [
      { key: "employeeCode", label: "Employee Code" }, { key: "name", label: "Name" }, { key: "email", label: "Email" },
      { key: "department", label: "Department" }, { key: "designation", label: "Designation" }, { key: "role", label: "Role" },
      { key: "joinDate", label: "Join Date" }, { key: "basicSalary", label: "Basic Salary" },
    ]);
    download("employee_report.csv", csv);
  });
  document.getElementById("exp-attendance").addEventListener("click", () => {
    const rows = att60.map(a => ({ ...a, name: getEmployee(a.employeeId).name, department: getEmployee(a.employeeId).department }));
    const csv = toCSV(rows, [
      { key: "date", label: "Date" }, { key: "name", label: "Name" }, { key: "department", label: "Department" },
      { key: "status", label: "Status" }, { key: "checkIn", label: "Check-in" }, { key: "checkOut", label: "Check-out" },
    ]);
    download("attendance_report.csv", csv);
  });
  document.getElementById("exp-leave").addEventListener("click", () => {
    const rows = store.leaveRequests.map(l => ({ ...l, name: getEmployee(l.employeeId).name, department: getEmployee(l.employeeId).department }));
    const csv = toCSV(rows, [
      { key: "name", label: "Name" }, { key: "department", label: "Department" }, { key: "leaveType", label: "Type" },
      { key: "startDate", label: "From" }, { key: "endDate", label: "To" }, { key: "status", label: "Status" }, { key: "adminComment", label: "Admin Comment" },
    ]);
    download("leave_report.csv", csv);
  });
};

/* ---------------- Init ---------------- */
render();
