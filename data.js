/* ============================================================
   Dayflow HRMS — seed / mock data generator
   Mirrors the schema used in database.py (employees, attendance,
   leave_requests) so the two implementations stay in sync.
   ============================================================ */

const DEPARTMENTS = ["Engineering", "Human Resources", "Sales", "Marketing", "Finance", "Operations"];

const DESIGNATIONS = {
  "Engineering": ["Software Engineer", "Senior Engineer", "Engineering Manager"],
  "Human Resources": ["HR Executive", "HR Manager"],
  "Sales": ["Sales Associate", "Sales Manager"],
  "Marketing": ["Marketing Executive", "Marketing Manager"],
  "Finance": ["Accountant", "Finance Manager"],
  "Operations": ["Operations Executive", "Operations Manager"],
};

const LEAVE_TYPES = ["Paid", "Sick", "Unpaid"];
const ATTENDANCE_STATUSES = ["Present", "Absent", "Half-day", "Leave"];

const FIRST_NAMES = ["Aarav", "Vivaan", "Isha", "Ananya", "Kabir", "Diya", "Reyansh", "Myra",
  "Arjun", "Saanvi", "Vihaan", "Anika", "Rohan", "Priya", "Karthik", "Neha"];
const LAST_NAMES = ["Sharma", "Verma", "Iyer", "Gupta", "Nair", "Reddy", "Menon", "Kapoor",
  "Joshi", "Rao", "Pillai", "Chowdhury", "Mehta", "Bose", "Das", "Singh"];

const STORAGE_KEY = "dayflow_hrms_v1";

function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function isoDate(d) { return d.toISOString().slice(0, 10); }
function addDays(date, days) { const d = new Date(date); d.setDate(d.getDate() + days); return d; }

function weightedStatus() {
  // Present 78%, Absent 6%, Half-day 10%, Leave 6%
  const r = Math.random() * 100;
  if (r < 78) return "Present";
  if (r < 84) return "Absent";
  if (r < 94) return "Half-day";
  return "Leave";
}

function generateSeedData(numEmployees = 24, attendanceDays = 45) {
  const employees = [];
  for (let i = 1; i <= numEmployees; i++) {
    const first = pick(FIRST_NAMES);
    const last = pick(LAST_NAMES);
    const dept = pick(DEPARTMENTS);
    const designation = pick(DESIGNATIONS[dept]);
    const basic = pick([28000, 35000, 42000, 55000, 68000, 82000]);
    const joinDate = addDays(new Date(), -randInt(60, 1500));

    employees.push({
      id: i,
      employeeCode: `DF${1000 + i}`,
      name: `${first} ${last}`,
      email: `${first.toLowerCase()}.${last.toLowerCase()}${i}@dayflow.com`,
      role: i === 1 ? "Admin" : "Employee",
      department: dept,
      designation: designation,
      phone: "",
      address: "",
      joinDate: isoDate(joinDate),
      basicSalary: basic,
      hra: Math.round(basic * 0.4),
      allowances: Math.round(basic * 0.15),
      deductions: Math.round(basic * 0.08),
    });
  }

  const attendance = [];
  let attId = 1;
  for (const emp of employees) {
    for (let d = 0; d < attendanceDays; d++) {
      const day = addDays(new Date(), -d);
      if (day.getDay() === 0 || day.getDay() === 6) continue; // skip weekends
      const status = weightedStatus();
      attendance.push({
        id: attId++,
        employeeId: emp.id,
        date: isoDate(day),
        status,
        checkIn: status === "Present" ? `09:1${randInt(0, 9)}` : null,
        checkOut: status === "Present" ? `18:0${randInt(0, 9)}` : null,
      });
    }
  }

  const leaveRequests = [];
  const sample = [...employees].sort(() => Math.random() - 0.5).slice(0, 10);
  const remarksPool = ["Family function", "Not feeling well", "Personal work", "Travel"];
  const statusPool = ["Pending", "Pending", "Approved", "Rejected"];
  sample.forEach((emp, idx) => {
    const start = addDays(new Date(), -randInt(0, 20));
    const end = addDays(start, randInt(0, 3));
    leaveRequests.push({
      id: idx + 1,
      employeeId: emp.id,
      leaveType: pick(LEAVE_TYPES),
      startDate: isoDate(start),
      endDate: isoDate(end),
      remarks: pick(remarksPool),
      status: pick(statusPool),
      adminComment: "",
    });
  });

  return { employees, attendance, leaveRequests };
}

function loadStore() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) {
    try { return JSON.parse(raw); } catch (e) { /* fall through to reseed */ }
  }
  const seeded = generateSeedData();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(seeded));
  return seeded;
}

function saveStore(store) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

function resetStore() {
  localStorage.removeItem(STORAGE_KEY);
  return loadStore();
}
