from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "hma_secret_key"

# ---------------------
# DATABASE INITIALIZATION
# ---------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Admin table (only you)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # Crew members table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS crew_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        crew TEXT,
        gojo TEXT
    )
    """)

    # Attendance table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        gojo TEXT,
        crew TEXT,
        member_name TEXT,
        status TEXT
    )
    """)

    # Schedule table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        gojo TEXT,
        crew TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------------
# CREATE DEFAULT ADMIN
# ---------------------
def create_admin():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin")
    admin_exists = cur.fetchone()
    if not admin_exists:
        cur.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            ("admin", "1234")
        )
    conn.commit()
    conn.close()

create_admin()

# ---------------------
# LOGIN PAGE
# ---------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )
        admin = cur.fetchone()
        conn.close()

        if admin:
            session["logged_in"] = True
            return redirect("/attendance")
    return render_template("login.html")

# ---------------------
# ATTENDANCE PAGE
# ---------------------
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if not session.get("logged_in"):
        return redirect("/")

    if request.method == "POST":
        date = request.form["date"]
        gojo = request.form["gojo"]
        crew = request.form["crew"]
        member = request.form["member"]
        status = request.form["status"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO attendance (date, gojo, crew, member_name, status) VALUES (?, ?, ?, ?, ?)",
            (date, gojo, crew, member, status)
        )
        conn.commit()
        conn.close()

    return render_template("attendance.html")

# ---------------------
# VIEW ATTENDANCE RECORDS
# ---------------------
@app.route("/records")
def records():
    if not session.get("logged_in"):
        return redirect("/")
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM attendance ORDER BY date DESC")
    data = cur.fetchall()
    conn.close()
    return render_template("records.html", data=data)

# ---------------------
# GOJO SCHEDULE GENERATOR
# ---------------------
@app.route("/schedule", methods=["GET", "POST"])
def schedule():
    if not session.get("logged_in"):
        return redirect("/")

    if request.method == "POST":
        gojos = request.form.getlist("gojo")
        crews = request.form.getlist("crew")

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        for i in range(len(crews)):
            cur.execute(
                "INSERT INTO schedule (date, gojo, crew) VALUES (date('now'), ?, ?)",
                (gojos[i % len(gojos)], crews[i])
            )
        conn.commit()
        conn.close()

    return render_template("schedule.html")

# ---------------------
# LOGOUT
# ---------------------
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")

# ---------------------
# RUN APP
# ---------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
