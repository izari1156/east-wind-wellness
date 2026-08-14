from datetime import date, datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

import db

app = Flask(__name__)
# Reads the secret key from an environment variable if you set one (recommended
# once this project is on GitHub), otherwise falls back to a default so the
# app still runs immediately for local/class use.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key-before-you-deploy")

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


#Shop details 

SHOP = {
    "name": "East Wind Wellness",
    "name_cn": "东风养生",
    "address": "335 Smith St, Singapore 050335",
    "phone": "6420 6767",
    "email": "hello@eastwindwellness.sg",
    "hours": "Monday - Saturday, 10:00am - 6:00pm",
    "facebook": "#",
    "instagram": "#",
}

# Team shown on the About Us page.
TEAM = [
    {
        "name": "Dr. Li Wei Ming",
        "title": "Founder & Senior TCM Physician",
        "photo": "team_li.png",
        "bio": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Dr. Li has over 20 years of clinical experience in herbal "
            "medicine and acupuncture. Replace this with a real bio."
        ),
    },
    {
        "name": "Dr. Chen Hui Fang",
        "title": "TCM Physician, Acupuncture",
        "photo": "team_chen.png",
        "bio": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Dr. Chen specialises in acupuncture for pain management and "
            "stress relief. Placeholder bio - please update."
        ),
    },
    {
        "name": "Dr. Tan Jia Le",
        "title": "TCM Physician, Herbal Prescription",
        "photo": "team_tan.png",
        "bio": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Dr. Tan focuses on personalised herbal formulas for chronic "
            "conditions. Placeholder bio text."
        ),
    },
    {
        "name": "Wong Mei Ling",
        "title": "Tui Na Massage Therapist",
        "photo": "team_wong.png",
        "bio": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Mei Ling is a certified Tui Na therapist who loves helping "
            "clients recover from muscle tension. Placeholder bio."
        ),
    },
    {
        "name": "Goh Zhi Hao",
        "title": "Clinic Manager",
        "photo": "team_goh.png",
        "bio": (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Zhi Hao keeps the clinic running smoothly and is usually the "
            "friendly face you'll meet at the front counter."
        ),
    },
]


def make_sure_database_ready():
    """Create the SQLite database file and starter data if missing."""
    if not db.database_exists():
        db.init_db()
    db.seed_if_empty()



#Auth helpers

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.", "error")
            return redirect(url_for("login", next=request.path))
        if session.get("role") != "admin":
            flash("That page is for shop admins only.", "error")
            return redirect(url_for("home"))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    return {
        "shop": SHOP,
        "current_user": {
            "id": session.get("user_id"),
            "name": session.get("full_name"),
            "role": session.get("role"),
        },
        "current_year": datetime.now().year,
    }


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



#pages, links

@app.route("/")
def home():
    conn = db.get_connection()
    herbs = conn.execute(
        "SELECT * FROM items WHERE category = 'herb' ORDER BY id LIMIT 3"
    ).fetchall()
    services = conn.execute(
        "SELECT * FROM items WHERE category = 'service' ORDER BY id LIMIT 3"
    ).fetchall()
    conn.close()
    return render_template("index.html", herbs=herbs, services=services)


@app.route("/products-services")
def products_services():
    conn = db.get_connection()
    herbs = conn.execute("SELECT * FROM items WHERE category = 'herb' ORDER BY id").fetchall()
    services = conn.execute("SELECT * FROM items WHERE category = 'service' ORDER BY id").fetchall()
    conn.close()
    return render_template("products_services.html", herbs=herbs, services=services)


@app.route("/about")
def about():
    return render_template("about.html", team=TEAM)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # This is a simple demo contact form - it doesn't send an email,
        # it just confirms to the visitor that we "received" the message.
        flash("Thanks for reaching out! We'll get back to you shortly.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")



#Auth: register / login / logout

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = []
        if not full_name or not email or not phone or not password:
            errors.append("Please fill in every field.")
        if password and len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if not errors:
            conn = db.get_connection()
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if existing:
                errors.append("An account with that email already exists.")
            else:
                conn.execute(
                    "INSERT INTO users (full_name, email, phone, password_hash, role) "
                    "VALUES (?, ?, ?, ?, 'user')",
                    (full_name, email, phone, generate_password_hash(password)),
                )
                conn.commit()
                conn.close()
                flash("Account created! You can now log in.", "success")
                return redirect(url_for("login"))
            conn.close()

        for e in errors:
            flash(e, "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = db.get_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['full_name']}!", "success")
            next_url = request.args.get("next")
            if user["role"] == "admin":
                return redirect(next_url or url_for("admin_dashboard"))
            return redirect(next_url or url_for("home"))

        flash("Incorrect email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))



#Appointment booking (for logged in customers)

@app.route("/book", methods=["GET", "POST"])
@login_required
def book_appointment():
    conn = db.get_connection()
    services = conn.execute(
        "SELECT * FROM items WHERE category = 'service' ORDER BY id"
    ).fetchall()

    if request.method == "POST":
        service_name = request.form.get("service_name", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()
        preferred_time = request.form.get("preferred_time", "").strip()
        notes = request.form.get("notes", "").strip()

        errors = []
        if not all([service_name, full_name, email, phone, preferred_date, preferred_time]):
            errors.append("Please fill in all required fields.")
        try:
            if preferred_date and date.fromisoformat(preferred_date) < date.today():
                errors.append("Please choose a date that is today or later.")
        except ValueError:
            errors.append("That date doesn't look right.")

        if not errors:
            conn.execute(
                "INSERT INTO appointments "
                "(user_id, service_name, full_name, email, phone, preferred_date, preferred_time, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    session["user_id"], service_name, full_name, email, phone,
                    preferred_date, preferred_time, notes,
                ),
            )
            conn.commit()
            conn.close()
            flash("Your appointment request has been sent! We'll confirm it shortly.", "success")
            return redirect(url_for("my_appointments"))

        for e in errors:
            flash(e, "error")

    conn.close()
    today_str = date.today().isoformat()
    return render_template("book_appointment.html", services=services, today=today_str)


@app.route("/my-appointments")
@login_required
def my_appointments():
    conn = db.get_connection()
    appointments = conn.execute(
        "SELECT * FROM appointments WHERE user_id = ? ORDER BY preferred_date, preferred_time",
        (session["user_id"],),
    ).fetchall()
    conn.close()
    return render_template("my_appointments.html", appointments=appointments)


@app.route("/my-appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    conn = db.get_connection()
    appt = conn.execute(
        "SELECT * FROM appointments WHERE id = ? AND user_id = ?",
        (appointment_id, session["user_id"]),
    ).fetchone()
    if appt and appt["status"] in ("pending", "confirmed"):
        conn.execute(
            "UPDATE appointments SET status = 'cancelled' WHERE id = ?", (appointment_id,)
        )
        conn.commit()
        flash("Appointment cancelled.", "success")
    else:
        flash("That appointment can't be cancelled.", "error")
    conn.close()
    return redirect(url_for("my_appointments"))



#Admin dashboard

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = db.get_connection()
    counts = {
        "pending": conn.execute(
            "SELECT COUNT(*) AS n FROM appointments WHERE status = 'pending'"
        ).fetchone()["n"],
        "confirmed": conn.execute(
            "SELECT COUNT(*) AS n FROM appointments WHERE status = 'confirmed'"
        ).fetchone()["n"],
        "total_appointments": conn.execute(
            "SELECT COUNT(*) AS n FROM appointments"
        ).fetchone()["n"],
        "total_users": conn.execute(
            "SELECT COUNT(*) AS n FROM users WHERE role = 'user'"
        ).fetchone()["n"],
        "total_items": conn.execute("SELECT COUNT(*) AS n FROM items").fetchone()["n"],
    }
    upcoming = conn.execute(
        "SELECT * FROM appointments WHERE status IN ('pending','confirmed') "
        "ORDER BY preferred_date, preferred_time LIMIT 5"
    ).fetchall()
    conn.close()
    return render_template("admin/dashboard.html", counts=counts, upcoming=upcoming)


@app.route("/admin/appointments")
@admin_required
def admin_appointments():
    status_filter = request.args.get("status", "all")
    conn = db.get_connection()
    if status_filter in ("pending", "confirmed", "completed", "cancelled"):
        appointments = conn.execute(
            "SELECT * FROM appointments WHERE status = ? ORDER BY preferred_date, preferred_time",
            (status_filter,),
        ).fetchall()
    else:
        appointments = conn.execute(
            "SELECT * FROM appointments ORDER BY preferred_date, preferred_time"
        ).fetchall()
    conn.close()
    return render_template(
        "admin/appointments.html", appointments=appointments, status_filter=status_filter
    )


@app.route("/admin/appointments/<int:appointment_id>/status", methods=["POST"])
@admin_required
def admin_update_appointment_status(appointment_id):
    new_status = request.form.get("status")
    if new_status not in ("pending", "confirmed", "completed", "cancelled"):
        flash("Unknown status.", "error")
        return redirect(url_for("admin_appointments"))
    conn = db.get_connection()
    conn.execute(
        "UPDATE appointments SET status = ? WHERE id = ?", (new_status, appointment_id)
    )
    conn.commit()
    conn.close()
    flash("Appointment updated.", "success")
    return redirect(request.referrer or url_for("admin_appointments"))


@app.route("/admin/items")
@admin_required
def admin_items():
    conn = db.get_connection()
    items = conn.execute("SELECT * FROM items ORDER BY category, id").fetchall()
    conn.close()
    return render_template("admin/items.html", items=items)


@app.route("/admin/items/new", methods=["GET", "POST"])
@admin_required
def admin_new_item():
    if request.method == "POST":
        category = request.form.get("category")
        name = request.form.get("name", "").strip()
        tagline = request.form.get("tagline", "").strip()
        description = request.form.get("description", "").strip()
        image_file = save_uploaded_image(request.files.get("image"))

        if category not in ("herb", "service") or not name:
            flash("Please choose a category and enter a name.", "error")
        else:
            conn = db.get_connection()
            conn.execute(
                "INSERT INTO items (category, name, tagline, description, image_file) "
                "VALUES (?, ?, ?, ?, ?)",
                (category, name, tagline, description, image_file or "logo.png"),
            )
            conn.commit()
            conn.close()
            flash("Item added.", "success")
            return redirect(url_for("admin_items"))

    return render_template("admin/item_form.html", item=None)


@app.route("/admin/items/<int:item_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_item(item_id):
    conn = db.get_connection()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if not item:
        conn.close()
        flash("Item not found.", "error")
        return redirect(url_for("admin_items"))

    if request.method == "POST":
        category = request.form.get("category")
        name = request.form.get("name", "").strip()
        tagline = request.form.get("tagline", "").strip()
        description = request.form.get("description", "").strip()
        uploaded = save_uploaded_image(request.files.get("image"))
        image_file = uploaded or item["image_file"]

        if category not in ("herb", "service") or not name:
            flash("Please choose a category and enter a name.", "error")
        else:
            conn.execute(
                "UPDATE items SET category=?, name=?, tagline=?, description=?, image_file=? "
                "WHERE id=?",
                (category, name, tagline, description, image_file, item_id),
            )
            conn.commit()
            conn.close()
            flash("Item updated.", "success")
            return redirect(url_for("admin_items"))

    conn.close()
    return render_template("admin/item_form.html", item=item)


@app.route("/admin/items/<int:item_id>/delete", methods=["POST"])
@admin_required
def admin_delete_item(item_id):
    conn = db.get_connection()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    flash("Item deleted.", "success")
    return redirect(url_for("admin_items"))


def save_uploaded_image(file_storage):
    """Save an uploaded image file if one was provided; return its filename."""
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        flash("Image must be a png, jpg, jpeg, gif or webp file.", "error")
        return None
    filename = secure_filename(file_storage.filename)
    # avoid overwriting an existing file with the same name
    base, ext = os.path.splitext(filename)
    candidate = filename
    i = 1
    while os.path.exists(os.path.join(UPLOAD_FOLDER, candidate)):
        candidate = f"{base}-{i}{ext}"
        i += 1
    file_storage.save(os.path.join(UPLOAD_FOLDER, candidate))
    return f"uploads/{candidate}"


if __name__ == "__main__":
    make_sure_database_ready()
    app.run(debug=True)
else:
    # to make sure the DB is ready if run through flask run
    make_sure_database_ready()
