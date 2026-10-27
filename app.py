from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import csv
import io
from flask import make_response

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def fetch_one(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def execute(query, params=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


@app.route("/")
def dashboard():
    today = date.today()
    total_students = fetch_one("SELECT COUNT(*) AS count FROM students")["count"]
    present_today = fetch_one(
        "SELECT COUNT(*) AS count FROM attendance WHERE attendance_date=%s AND status='Present'",
        (today,),
    )["count"]
    absent_today = fetch_one(
        "SELECT COUNT(*) AS count FROM attendance WHERE attendance_date=%s AND status='Absent'",
        (today,),
    )["count"]

    recent = fetch_all("""
        SELECT s.id, s.roll_no, s.full_name, a.status, a.attendance_date
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        ORDER BY a.attendance_date DESC, s.roll_no
        LIMIT 10
    """)

    return render_template(
        "dashboard.html",
        today=today,
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        recent=recent,
    )


@app.route("/mark-attendance", methods=["GET", "POST"])
def mark_attendance():
    students = fetch_all(
        "SELECT id, roll_no, full_name FROM students ORDER BY roll_no"
    )

    # Get selected date
    selected_date = request.args.get(
        "attendance_date",
        date.today().isoformat()
    )

    conn = None
    cursor = None

    # SAVE attendance
    if request.method == "POST":
        selected_date = request.form.get(
            "attendance_date",
            date.today().isoformat()
        )

        try:
            selected_date_obj = datetime.strptime(
                selected_date, "%Y-%m-%d"
            ).date()

            conn = get_db_connection()
            cursor = conn.cursor()

            for student in students:
                status = request.form.get(
                    f"status_{student['id']}"
                )

                if status in ("Present", "Absent"):
                    cursor.execute(
                        """
                        INSERT INTO attendance
                            (student_id, attendance_date, status)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            status = VALUES(status)
                        """,
                        (
                            student["id"],
                            selected_date_obj,
                            status
                        )
                    )

            conn.commit()

            flash(
                f"Attendance saved for "
                f"{selected_date_obj.strftime('%d %b %Y')}.",
                "success"
            )

        except (ValueError, Error) as exc:
            if conn:
                conn.rollback()

            flash(
                f"Could not save attendance: {exc}",
                "danger"
            )

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return redirect(
            url_for(
                "mark_attendance",
                attendance_date=selected_date
            )
        )

    # LOAD attendance for selected date
    try:
        selected_date_obj = datetime.strptime(
            selected_date, "%Y-%m-%d"
        ).date()

        existing_rows = fetch_all(
            """
            SELECT student_id, status
            FROM attendance
            WHERE attendance_date = %s
            """,
            (selected_date_obj,)
        )
        print("Selected date:", selected_date_obj)
        print("Existing attendance:", existing_rows)

        existing = {
            row["student_id"]: row["status"]
            for row in existing_rows
        }

    except ValueError:
        selected_date = date.today().isoformat()
        existing = {}

        flash("Invalid date selected.", "warning")

    return render_template(
        "mark_attendance.html",
        students=students,
        selected_date=selected_date,
        existing=existing
    )



@app.route("/reports")
def reports():
    from_date = request.args.get(
        "from_date",
        date.today().replace(day=1).isoformat()
    )
    to_date = request.args.get(
        "to_date",
        date.today().isoformat()
    )

    summary = fetch_all("""
        SELECT s.id, s.roll_no, s.full_name, COUNT(a.id) AS total_marked, SUM(a.status='Present') AS present_count,
            SUM(a.status='Absent') AS absent_count
        FROM students s
        LEFT JOIN attendance a
            ON a.student_id = s.id
            AND a.attendance_date BETWEEN %s AND %s
        GROUP BY s.id, s.roll_no, s.full_name
        ORDER BY s.roll_no
    """, (from_date, to_date))

    for row in summary:
        total = row["total_marked"] or 0
        present = row["present_count"] or 0
        absent = row["absent_count"] or 0

        row["total_marked"] = total
        row["present_count"] = present
        row["absent_count"] = absent
        row["percentage"] = round(
            (present / total) * 100, 1
        ) if total else 0

    # Download report when Generate Report is clicked
    if request.args.get("download") == "1":
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Roll No","Student Name","Total Marked","Present","Absent","Percentage"])

        for row in summary:
            writer.writerow([row["roll_no"], row["full_name"], row["total_marked"], row["present_count"], row["absent_count"],
                f'{row["percentage"]}%'
            ])

        response = make_response(
            "\ufeff" + output.getvalue()
        )
        response.headers["Content-Type"] = (
            "text/csv; charset=utf-8"
        )
        response.headers["Content-Disposition"] = (
            f"attachment; filename=attendance_report_"
            f"{from_date}_to_{to_date}.csv"
        )

        return response

    return render_template(
        "reports.html",summary=summary,from_date=from_date,to_date=to_date
    )

@app.route("/student/<int:student_id>")
def student_history(student_id):
    student = fetch_one("SELECT * FROM students WHERE id=%s", (student_id,))
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("reports"))

    history = fetch_all("""
        SELECT attendance_date, status
        FROM attendance
        WHERE student_id=%s
        ORDER BY attendance_date DESC
    """, (student_id,))

    total = len(history)
    present = sum(1 for row in history if row["status"] == "Present")
    percentage = round((present / total) * 100, 1) if total else 0

    return render_template(
        "student.html",
        student=student,
        history=history,
        total=total,
        present=present,
        absent=total-present,
        percentage=percentage,
    )


@app.route("/download-student-history/<int:student_id>")
def download_student_history(student_id):
    student = fetch_one(
        """
        SELECT id, roll_no, full_name, course, email
        FROM students
        WHERE id = %s
        """,
        (student_id,)
    )

    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("reports"))

    history = fetch_all(
        """
        SELECT attendance_date, status
        FROM attendance
        WHERE student_id = %s
        ORDER BY attendance_date DESC
        """,
        (student_id,)
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Student Attendance Report"])
    writer.writerow(["Roll Number", student["roll_no"]])
    writer.writerow(["Student Name", student["full_name"]])
    writer.writerow(["Course", student["course"]])
    writer.writerow(["Email", student["email"] or ""])
    writer.writerow([])
    writer.writerow(["Attendance Date", "Status"])

    for row in history:
        attendance_date = row["attendance_date"]

        if hasattr(attendance_date, "strftime"):
            attendance_date = attendance_date.strftime("%d-%b-%Y")

        writer.writerow([attendance_date, row["status"]])

    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{student["roll_no"]}_attendance_report.csv"'
    )

    return response







@app.errorhandler(Error)
def database_error(error):
    return render_template("error.html", error=error), 500





# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    try:
        conn = get_db_connection()

        if conn.is_connected():
            print("MySQL Connected Successfully!")

            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            print("Connected Database:", cursor.fetchone()[0])

            cursor.close()
            conn.close()

    except Error as e:
        print("MySQL Connection Error:", e)

    app.run(debug=True)
