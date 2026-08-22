# NovaHR Python HR Dashboard

NovaHR is a dependency-free Python and SQLite HR dashboard with separate Employee, HR, and Admin experiences.

## Features

- Employee, HR, and Admin authentication
- Extra PIN verification for admins
- Employee leave application workflow
- Immediate admin leave-notification count
- Admin approve/deny decisions
- Employee-visible leave status and reviewer
- Personal attendance and payroll views
- Admin access to all payroll records
- Salary-structure editing with validation
- SQLite constraints and indexed queries
- Nine sample users and realistic demo data

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run:

   ```bash
   python app.py
   ```

4. Open <http://localhost:8000>.

The `novahr.db` database is created automatically the first time the application runs.

## Admin demo account

- Role: `Admin`
- Email: `admin@novahr.demo`
- Password: `Admin@123`
- PIN: `4826`

See [TEST_ACCOUNTS.md](TEST_ACCOUNTS.md) for every sample login.

## Upload to GitHub

Create an empty GitHub repository, then run these commands from this folder:

```bash
git init
git add .
git commit -m "Add NovaHR Python HR dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your GitHub details.

## Important

This is an educational demo. Before production use, add HTTPS, persistent server-side sessions, CSRF protection, environment-managed secrets, audit logging, and production-grade password hashing such as Argon2 or bcrypt.
