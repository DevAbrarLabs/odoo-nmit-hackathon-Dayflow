# Dayflow HRMS — Admin Console (Website Version)

Same scope as before — Admin dashboard, employee list, employee details,
attendance overview, leave approvals, payroll management, analytics &
reports — rebuilt as a **static website**: plain HTML, CSS, and
vanilla JavaScript. No build step, no framework, no server required.

## Run it

Just open `index.html` in a browser — or, for the cleanest experience
(so relative links behave exactly like a deployed site), serve the
folder locally:

```bash
# from inside this folder
python -m http.server 8000
# then open http://localhost:8000
```

Data (employees, attendance, leave requests) is generated on first
load and kept in the browser's `localStorage`, so edits persist across
reloads on the same machine/browser. To reset to fresh mock data, clear
your browser's site data for this page (or run `resetStore()` in the
browser console).

## Files

| File          | Purpose                                                        |
|---------------|-----------------------------------------------------------------|
| `index.html`  | Page shell: sidebar nav + content mount point                  |
| `styles.css`  | Design system — colors, type, cards, tables, badges, charts     |
| `data.js`     | Seed/mock data generator + localStorage read/write helpers      |
| `app.js`      | Hash-based router + all 7 page renderers + CRUD interactions    |

## Pages

1. **Admin Dashboard** — headline metrics, department chart, recent leave requests, today's attendance
2. **Employee List** — searchable/filterable table, add-employee form, click a row to open Employee Details
3. **Employee Details** — profile edit, salary structure, attendance/leave history (tabs)
4. **Attendance Overview** — filterable log + status breakdown chart, manual admin override
5. **Leave Approvals** — approve/reject with comments, full history tab
6. **Payroll Management** — salary table, edit structure, generate a downloadable salary slip
7. **Analytics & Reports** — attendance/leave/payroll charts + CSV export

## Deploying

This is a plain static site — it works as-is on **GitHub Pages**,
Netlify, Vercel, or any static host:

```bash
# GitHub Pages, from your repo root
git add index.html styles.css data.js app.js README.md
git commit -m "Add admin/HR web console"
git push
# then enable Pages for this repo/branch in GitHub Settings → Pages
```

## Notes for merging with teammates

- This UI currently reads/writes `localStorage` directly so it works
  standalone for the demo. When the team's backend/auth API is ready,
  swap the calls in `data.js` (`loadStore`/`saveStore`) for `fetch()`
  calls to that API — the rendering code in `app.js` doesn't need to
  change, since it just reads from the in-memory `store` object.
- Each employee has a `role` field (`"Admin"` / `"Employee"`) meant to
  line up with whatever the auth module produces — gate this console
  behind `role === "Admin"` once that's wired in.
