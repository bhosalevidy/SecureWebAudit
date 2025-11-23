from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from scanner.selenium_test import run_selenium_tests
from scanner.security import https_check, security_headers_check, cookie_flags_check, xss_check, sqli_check
import sqlite3, random, smtplib, time, os, json
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
from threading import Thread
from ai_summary import generate_summary

# ---------------- Load environment ----------------
load_dotenv()
app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = "users.db"

# ---------------- Helper ----------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- OTP ----------------
def generate_otp(length=6):
    return ''.join([str(random.randint(0,9)) for _ in range(length)])

def send_async_email(app, msg, sender_email, sender_password):
    with app.app_context():
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print("Error sending OTP:", e)

def send_otp_email(receiver_email, otp):
    sender_email = os.environ.get("GMAIL_EMAIL")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender_email or not sender_password:
        raise Exception("Gmail credentials not found in environment variables!")
    msg = MIMEText(f"Your OTP for SecureWebAudit registration is: {otp}")
    msg['Subject'] = "SecureWebAudit OTP Verification"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    Thread(target=send_async_email, args=(app, msg, sender_email, sender_password)).start()

# ---------------- Email Validation ----------------
def is_valid_email(email):
    try:
        v = validate_email(email)
        return True, v["email"]
    except EmailNotValidError as e:
        return False, str(e)

# ---------------- Routes ----------------
@app.route("/")
def home():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if not username or not password:
            flash("Please enter both username and password.", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and user["verified"] == 1 and check_password_hash(user["password"], password):
            session["user"] = username
            session["user_email"] = user["email"]
            flash("Login successful!", "success")
            return redirect(url_for("input_page"))
        else:
            flash("Invalid username/password or account not verified.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not fullname or not email or not username or not password:
            flash("All fields are required!", "error")
            return redirect(url_for("register"))

        valid, result = is_valid_email(email)
        if not valid:
            flash(f"Invalid email: {result}", "error")
            return redirect(url_for("register"))
        email = result

        conn = get_db_connection()
        if conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone():
            flash("Username already exists!", "error")
            conn.close()
            return redirect(url_for("register"))
        if conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone():
            flash("Email already exists!", "error")
            conn.close()
            return redirect(url_for("register"))

        hashed_pwd = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (fullname, email, username, password, verified) VALUES (?, ?, ?, ?, ?)",
            (fullname, email, username, hashed_pwd, 0)
        )
        conn.commit()
        conn.close()

        otp = generate_otp()
        session["otp"] = otp
        session["email"] = email
        session["otp_time"] = time.time()
        send_otp_email(email, otp)

        flash("OTP sent to your email. Please verify to activate your account.")
        return redirect(url_for("verify_otp"))

    return render_template("register.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = ''.join([request.form.get(f'otp{i}', '') for i in range(1,7)]).strip()
        if time.time() - session.get("otp_time", 0) > 300:
            flash("OTP expired. Please register again.", "error")
            session.pop("otp", None)
            session.pop("email", None)
            return redirect(url_for("register"))
        if entered_otp == session.get("otp"):
            conn = get_db_connection()
            conn.execute("UPDATE users SET verified=1 WHERE email=?", (session["email"],))
            conn.commit()
            conn.close()
            flash("Account verified! You can login now.", "success")
            session.pop("otp")
            session.pop("email")
            return redirect(url_for("login"))
        else:
            flash("Invalid OTP.", "error")
    return render_template("otp.html")

@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    if "email" not in session:
        flash("Session expired. Please register again.", "error")
        return redirect(url_for("register"))

    otp = generate_otp()
    session["otp"] = otp
    session["otp_time"] = time.time()
    send_otp_email(session["email"], otp)
    flash("A new OTP has been sent to your email.", "success")
    return redirect(url_for("verify_otp"))

@app.route("/input")
def input_page():
    return render_template("input.html")

@app.route("/dashboard", methods=["POST"])
def dashboard():
    url = request.form.get("url")
    if not url:
        return "No URL provided", 400

    # --- Run Selenium Functional Tests ---
    results = run_selenium_tests(url)
    results.setdefault("pass", 0)
    results.setdefault("fail", 0)
    results.setdefault("error", "")
    results.setdefault("details", [])

    # --- Add type field for Selenium tests ---
    for test in results["details"]:
        test["type"] = "selenium"

    # --- Run Security Checks ---
    sec_results = [
        https_check(url),
        security_headers_check(url),
        cookie_flags_check(url),
        xss_check(url),
        sqli_check(url)
    ]
    for r in sec_results:
        r["type"] = "security"

    results["details"].extend(sec_results)

    # Count pass/fail for security
    sec_pass = sum(1 for r in sec_results if r["status"] == "pass")
    sec_fail = sum(1 for r in sec_results if r["status"] == "fail")
    results["security"] = {"pass": sec_pass, "fail": sec_fail, "details": sec_results}

    # Save results to JSON
    try:
        os.makedirs("reports", exist_ok=True)
        with open("reports/scan_results.json", "w") as f:
            json.dump(results, f, indent=4)
    except Exception as e:
        print("Error saving results:", e)

    ai_summary = generate_summary()
    return render_template("dashboard.html", test_results=results, url=url, ai_summary=ai_summary)


@app.route("/get_summary")
def get_summary():
    try:
        # Always read the latest summary from the JSON file
        summary = generate_summary("reports/scan_results.json")
        return jsonify({"summary": summary})
    except Exception as e:
        print("Error generating summary:", e)
        return jsonify({"summary": "Error generating summary."})


@app.route('/send_ai_report', methods=['POST'])
def send_ai_report():
    data = request.get_json()
    report = data.get('report')
    if not report:
        return jsonify({"status": "error", "message": "❌ No report text provided."})
    user_email = session.get("user_email")
    if not user_email:
        return jsonify({"status": "error", "message": "❌ You are not logged in. Please log in again."})
    sender_email = os.environ.get("GMAIL_EMAIL")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not sender_email or not sender_password:
        return jsonify({"status": "error", "message": "❌ Gmail sender credentials are missing in .env file."})
    try:
        msg = MIMEText(report, "plain")
        msg['Subject'] = "📄 Your SecureWebAudit AI Report"
        msg['From'] = sender_email
        msg['To'] = user_email
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender_email, sender_password)
        except:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
        return jsonify({"status": "success", "message": f"✅ Report sent to {user_email}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ Failed to send report: {str(e)}"})

@app.route("/help")
def help_page():
    return render_template("help.html")

@app.route("/all_users")
def admin_page():
    conn = get_db_connection()
    users = conn.execute("SELECT id, fullname, username, email, verified FROM users").fetchall()
    conn.close()
    return render_template("all_users.html", users=users)

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully!", "success")
    return redirect(url_for("admin_page"))

@app.route("/test")
def test():
    return "Flask is running!"

if __name__ == "__main__":
    app.run(debug=True)
