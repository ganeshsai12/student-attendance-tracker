# Student Attendance Tracker

Beginner-friendly Flask + MySQL attendance management project.

## Features

- Dashboard with today's attendance summary
- Mark Present/Absent for a selected date
- Update an existing day's attendance
- Attendance reports with date range
- Individual student attendance history
- Bootstrap responsive UI
- Sample students and attendance data
- MySQL using `mysql-connector-python`

## Project structure

```text
student_attendance_tracker/
├── app.py
├── config.py
├── requirements.txt
├── schema.sql
├── README.md
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── mark_attendance.html
│   ├── reports.html
│   ├── student.html
│   └── error.html
└── static/
    └── css/
        └── style.css
```

## Local setup

1. Install Python 3.10+ and MySQL 8+.
2. Create a virtual environment.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Edit `config.py` and put your MySQL username/password.
5. Create the database and sample data:
   - MySQL command line: `mysql -u root -p < schema.sql`
   - Or open `schema.sql` in MySQL Workbench and run it.
6. Start Flask:
   `python app.py`
7. Open:
   `http://127.0.0.1:5000`

## Important

The sample data uses dates in September 2026. The dashboard always shows today's date and counts attendance only if today's records exist.

For production deployment, do not use Flask's debug server. Set a strong secret key, use environment variables for database credentials, and run behind a production WSGI server/reverse proxy.
