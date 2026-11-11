"""
Alumni portal for PM SHRI Kendriya Vidyalaya No. 2 Pondicherry.

Run:  python app.py          (http://127.0.0.1:5000)
"""

import os
import secrets
import time
from datetime import datetime
from functools import wraps

from flask import (Flask, abort, flash, g, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import db
from core import (CLASSES, EMAIL_RE, JOB_TYPES, SCHOOL, STREAMS, _failed_logins, csrf_token, is_locked,
                  profile_fields_from, safe_next, safe_url, save_photo, validate_password, validate_profile)
from db import execute, query, requires_approval
from notify import notify_new_post

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


def _load_secret_key():
    """Use SECRET_KEY env var, else a key generated once and kept in instance/."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    key_file = os.path.join(INSTANCE_DIR, "secret_key")
    if not os.path.exists(key_file):
        with open(key_file, "w") as f:
            f.write(secrets.token_hex(32))
    with open(key_file) as f:
        return f.read().strip()


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=_load_secret_key(),
        DATABASE=os.environ.get("PORTAL_DB") or os.path.join(INSTANCE_DIR, "portal.db"),
        UPLOAD_FOLDER=os.path.join(INSTANCE_DIR, "uploads"),
        MAX_CONTENT_LENGTH=3 * 1024 * 1024,
        REQUIRE_APPROVAL=os.environ.get("REQUIRE_APPROVAL", "1") != "0",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE") == "1",
        # Stay signed in: the cookie lasts 30 days and is renewed on every visit, so active members never get logged out.
        PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 30,
        SESSION_REFRESH_EACH_REQUEST=True,
    )
    if config:
        app.config.update(config)

    db.init_db(app.config["DATABASE"])
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.teardown_appcontext(db.close_db)
    register_routes(app)
    from api import bp as api_bp
    app.register_blueprint(api_bp)
    return app


# ---------------------------------------------------------------- helpers

# Public API reads that are identical for every visitor and may be cached by Vercel's CDN.
EDGE_CACHED = {"/api/home"}


def current_user():
    return g.get("user")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please sign in to continue.", "info")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def approved_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user()["status"] != "approved":
            return redirect(url_for("pending"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user()["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def form(name, default=""):
    return (request.form.get(name) or default).strip()


# ---------------------------------------------------------------- routes

def register_routes(app):

    @app.before_request
    def load_user_and_check_csrf():
        g.user = None
        # Only touch the session when the browser sent one: reading it makes Flask add "Vary: Cookie",
        # which stops Vercel from caching public responses for signed-out visitors.
        has_session = app.config["SESSION_COOKIE_NAME"] in request.cookies
        uid = session.get("uid") if has_session else None
        if uid and not session.permanent:
            session.permanent = True  # upgrade sign-ins made before "stay signed in" existed
        if uid:
            user = query("SELECT * FROM users WHERE id = ?", (uid,), one=True)
            if user and user["status"] in ("suspended", "rejected"):
                session.clear()
            else:
                g.user = user
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # HTML forms send csrf_token; the React frontend sends the X-CSRF-Token header
            token = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
            expected = session.get("csrf")
            if not expected or not secrets.compare_digest(token, expected):
                abort(400, "Invalid or missing form token. Please reload the page and try again.")

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        if request.path.startswith("/api/") and "Cache-Control" not in resp.headers:
            signed_out = app.config["SESSION_COOKIE_NAME"] not in request.cookies
            if request.method == "GET" and request.path in EDGE_CACHED and signed_out and resp.status_code == 200:
                # Same for everyone, so Vercel's CDN may answer it for 30s (and serve it stale while refreshing)
                resp.headers["Cache-Control"] = "public, max-age=0, s-maxage=30, stale-while-revalidate=300"
                # Vercel only caches responses it proxies from another server (our /api rewrite) when asked to
                resp.headers["Vercel-CDN-Cache-Control"] = "max-age=30, stale-while-revalidate=300"
                resp.headers["x-vercel-enable-rewrite-caching"] = "1"
            else:
                resp.headers["Cache-Control"] = "private, no-cache"
        return resp

    @app.context_processor
    def inject_globals():
        pending_count = 0
        if current_user() and current_user()["role"] == "admin":
            pending_count = query("SELECT COUNT(*) c FROM users WHERE status='pending'", one=True)["c"]
        return {
            "school": SCHOOL,
            "user": current_user(),
            "csrf_token": csrf_token(),
            "pending_count": pending_count,
            "require_approval": requires_approval(),
            "now_year": datetime.now().year,
        }

    @app.template_filter("datefmt")
    def datefmt(value, fmt="%d %b %Y"):
        if not value:
            return ""
        try:
            return datetime.fromisoformat(value.replace(" ", "T")).strftime(fmt)
        except ValueError:
            return value

    @app.template_filter("initials")
    def initials(name):
        parts = [p for p in (name or "?").split() if p]
        return "".join(p[0] for p in parts[:2]).upper()

    # ---- public

    @app.route("/")
    def index():
        stats = {
            "alumni": query("SELECT COUNT(*) c FROM users WHERE status='approved'", one=True)["c"],
            "batches": query("SELECT COUNT(DISTINCT batch_year) c FROM users WHERE status='approved'", one=True)["c"],
            "mentors": query("SELECT COUNT(*) c FROM users WHERE status='approved' AND willing_to_mentor=1", one=True)["c"],
            "events": query("SELECT COUNT(*) c FROM events WHERE starts_at >= ?", (datetime.now().strftime("%Y-%m-%dT%H:%M"),), one=True)["c"],
        }
        news = query("SELECT * FROM announcements ORDER BY created_at DESC, id DESC LIMIT 3")
        events = query("SELECT * FROM events WHERE starts_at >= ? ORDER BY starts_at LIMIT 3",
                       (datetime.now().strftime("%Y-%m-%dT%H:%M"),))
        return render_template("index.html", stats=stats, news=news, events=events)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user():
            return redirect(url_for("dashboard"))
        values = {}
        if request.method == "POST":
            values = profile_fields_from(request.form)
            email = form("email").lower()
            password = request.form.get("password", "")
            values["email"] = email
            error = validate_profile(values)
            if not error and not EMAIL_RE.match(email):
                error = "Please enter a valid email address."
            if not error:
                error = validate_password(password)
            if not error and password != request.form.get("confirm_password", ""):
                error = "Passwords do not match."
            if not error and not request.form.get("agree"):
                error = "Please confirm that you are an alumnus/alumna of the school."
            if not error and query("SELECT 1 FROM users WHERE email = ?", (email,), one=True):
                error = "An account with this email already exists. Try signing in."
            if error:
                flash(error, "error")
            else:
                status = "pending" if requires_approval() else "approved"
                uid = execute(
                    """INSERT INTO users (name, email, password_hash, phone, batch_year, last_class,
                        stream, house, admission_no, city, country, occupation, organization,
                        industry, linkedin, bio, willing_to_mentor, show_contact, status)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (values["name"], email, generate_password_hash(password), values["phone"],
                     int(values["batch_year"]), values["last_class"], values["stream"], values["house"],
                     values["admission_no"], values["city"], values["country"], values["occupation"],
                     values["organization"], values["industry"], values["linkedin"], values["bio"],
                     values["willing_to_mentor"], values["show_contact"], status))
                session.clear()
                session["uid"] = uid
                session.permanent = True
                flash("Welcome aboard! Your account has been created.", "success")
                return redirect(url_for("dashboard"))
        return render_template("signup.html", v=values, streams=STREAMS, classes=CLASSES)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user():
            return redirect(url_for("dashboard"))
        email = ""
        if request.method == "POST":
            email = form("email").lower()
            password = request.form.get("password", "")
            key = f"{request.remote_addr}|{email}"
            if is_locked(key):
                flash("Too many failed attempts. Please wait 10 minutes and try again.", "error")
            else:
                user = query("SELECT * FROM users WHERE email = ?", (email,), one=True)
                if user and check_password_hash(user["password_hash"], password):
                    if user["status"] == "suspended":
                        flash("This account has been suspended. Please contact the school.", "error")
                    elif user["status"] == "rejected":
                        flash("Your registration was not approved. Please contact the school.", "error")
                    else:
                        _failed_logins.pop(key, None)
                        session.clear()
                        session["uid"] = user["id"]
                        session.permanent = True
                        execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user["id"],))
                        flash(f"Welcome back, {user['name'].split()[0]}!", "success")
                        return redirect(safe_next(request.args.get("next")) or url_for("dashboard"))
                else:
                    _failed_logins[key].append(time.time())
                    flash("Incorrect email or password.", "error")
        return render_template("login.html", email=email)

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("You have been signed out.", "info")
        return redirect(url_for("index"))

    @app.route("/pending")
    @login_required
    def pending():
        if current_user()["status"] == "approved":
            return redirect(url_for("dashboard"))
        return render_template("pending.html")

    # ---- members

    @app.route("/dashboard")
    @approved_required
    def dashboard():
        u = current_user()
        now = datetime.now().strftime("%Y-%m-%dT%H:%M")
        batchmates = query("""SELECT * FROM users WHERE status='approved' AND batch_year=? AND id<>?
                              ORDER BY name LIMIT 8""", (u["batch_year"], u["id"]))
        events = query("""SELECT e.*, (SELECT COUNT(*) FROM rsvps r WHERE r.event_id=e.id) going,
                                 EXISTS(SELECT 1 FROM rsvps r WHERE r.event_id=e.id AND r.user_id=?) mine
                          FROM events e WHERE starts_at >= ? ORDER BY starts_at LIMIT 3""", (u["id"], now))
        news = query("SELECT * FROM announcements ORDER BY created_at DESC, id DESC LIMIT 3")
        jobs = query("""SELECT j.*, u.name poster FROM jobs j JOIN users u ON u.id=j.posted_by
                        WHERE is_open=1 ORDER BY j.created_at DESC, j.id DESC LIMIT 4""")
        filled = sum(1 for f in ("phone", "city", "occupation", "organization", "bio", "photo", "stream", "linkedin") if u[f])
        completeness = int(filled / 8 * 100)
        return render_template("dashboard.html", batchmates=batchmates, events=events, news=news,
                               jobs=jobs, completeness=completeness)

    @app.route("/directory")
    @approved_required
    def directory():
        q, batch, city = request.args.get("q", "").strip(), request.args.get("batch", "").strip(), request.args.get("city", "").strip()
        mentor = request.args.get("mentor") == "1"
        sql, args = "SELECT * FROM users WHERE status='approved'", []
        if q:
            like = f"%{q}%"
            sql += " AND (name LIKE ? OR occupation LIKE ? OR organization LIKE ? OR industry LIKE ?)"
            args += [like] * 4
        if batch.isdigit():
            sql += " AND batch_year = ?"
            args.append(int(batch))
        if city:
            sql += " AND city LIKE ?"
            args.append(f"%{city}%")
        if mentor:
            sql += " AND willing_to_mentor = 1"
        sql += " ORDER BY batch_year DESC, name LIMIT 300"
        people = query(sql, args)
        batches = [r["batch_year"] for r in query(
            "SELECT DISTINCT batch_year FROM users WHERE status='approved' ORDER BY batch_year DESC")]
        return render_template("directory.html", people=people, batches=batches,
                               q=q, batch=batch, city=city, mentor=mentor)

    @app.route("/alumni/<int:uid>")
    @approved_required
    def profile(uid):
        person = query("SELECT * FROM users WHERE id=? AND status='approved'", (uid,), one=True)
        if not person:
            abort(404)
        memories = query("SELECT * FROM memories WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (uid,))
        jobs = query("SELECT * FROM jobs WHERE posted_by=? AND is_open=1 ORDER BY created_at DESC", (uid,))
        return render_template("profile.html", p=person, memories=memories, jobs=jobs)

    @app.route("/profile/edit", methods=["GET", "POST"])
    @login_required
    def edit_profile():
        u = current_user()
        if request.method == "POST":
            values = profile_fields_from(request.form)
            error = validate_profile(values)
            photo, photo_err = save_photo(request.files.get("photo"), app.config["UPLOAD_FOLDER"])
            error = error or photo_err
            if error:
                flash(error, "error")
                return render_template("profile_edit.html", v={**dict(u), **values},
                                       streams=STREAMS, classes=CLASSES)
            values["batch_year"] = int(values["batch_year"])
            cols = list(values.keys())
            sets = ", ".join(f"{c}=?" for c in cols)
            params = [values[c] for c in cols]
            if photo:
                sets += ", photo=?"
                params.append(photo)
                if u["photo"]:
                    old = os.path.join(app.config["UPLOAD_FOLDER"], u["photo"])
                    if os.path.exists(old):
                        os.remove(old)
            execute(f"UPDATE users SET {sets} WHERE id=?", (*params, u["id"]))
            flash("Profile updated.", "success")
            return redirect(url_for("profile", uid=u["id"]) if u["status"] == "approved" else url_for("pending"))
        return render_template("profile_edit.html", v=dict(u), streams=STREAMS, classes=CLASSES)

    @app.route("/settings/password", methods=["GET", "POST"])
    @login_required
    def change_password():
        if request.method == "POST":
            u = current_user()
            new = request.form.get("new_password", "")
            if not check_password_hash(u["password_hash"], request.form.get("current_password", "")):
                flash("Your current password is incorrect.", "error")
            elif validate_password(new):
                flash(validate_password(new), "error")
            elif new != request.form.get("confirm_password", ""):
                flash("New passwords do not match.", "error")
            else:
                execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(new), u["id"]))
                flash("Password changed successfully.", "success")
                return redirect(url_for("dashboard"))
        return render_template("password.html")

    @app.route("/uploads/<path:filename>")
    @login_required
    def uploaded_file(filename):
        resp = send_from_directory(app.config["UPLOAD_FOLDER"], filename)
        # Uploads get a new random name whenever they change, so browsers can keep them for a year.
        resp.headers["Cache-Control"] = "private, max-age=31536000, immutable"
        return resp

    # ---- events

    @app.route("/events")
    @approved_required
    def events():
        now = datetime.now().strftime("%Y-%m-%dT%H:%M")
        base = """SELECT e.*, (SELECT COUNT(*) FROM rsvps r WHERE r.event_id=e.id) going,
                         EXISTS(SELECT 1 FROM rsvps r WHERE r.event_id=e.id AND r.user_id=?) mine
                  FROM events e"""
        upcoming = query(base + " WHERE starts_at >= ? ORDER BY starts_at", (current_user()["id"], now))
        past = query(base + " WHERE starts_at < ? ORDER BY starts_at DESC LIMIT 10", (current_user()["id"], now))
        return render_template("events.html", upcoming=upcoming, past=past)

    @app.route("/events/<int:eid>")
    @approved_required
    def event_detail(eid):
        event = query("""SELECT e.*, EXISTS(SELECT 1 FROM rsvps r WHERE r.event_id=e.id AND r.user_id=?) mine
                         FROM events e WHERE id=?""", (current_user()["id"], eid), one=True)
        if not event:
            abort(404)
        attendees = query("""SELECT u.id, u.name, u.batch_year, u.photo FROM rsvps r
                             JOIN users u ON u.id=r.user_id WHERE r.event_id=? ORDER BY r.created_at""", (eid,))
        return render_template("event_detail.html", e=event, attendees=attendees,
                               is_past=event["starts_at"] < datetime.now().strftime("%Y-%m-%dT%H:%M"))

    @app.route("/events/new", methods=["GET", "POST"])
    @admin_required
    def new_event():
        v = {}
        if request.method == "POST":
            v = {k: form(k) for k in ("title", "description", "location", "starts_at")}
            try:
                datetime.fromisoformat(v["starts_at"])
                valid_date = True
            except ValueError:
                valid_date = False
            if not all(v.values()):
                flash("All fields are required.", "error")
            elif not valid_date:
                flash("Please pick a valid date and time.", "error")
            else:
                eid = execute("INSERT INTO events (title, description, location, starts_at, created_by) VALUES (?,?,?,?,?)",
                              (v["title"], v["description"], v["location"], v["starts_at"][:16], current_user()["id"]))
                when = v["starts_at"].replace("T", " ")
                notify_new_post("event", v["title"], f"{v['location']} · {when}\n{v['description']}",
                                f"/events/{eid}", current_user()["id"])
                flash("Event published.", "success")
                return redirect(url_for("event_detail", eid=eid))
        return render_template("event_form.html", v=v)

    @app.route("/events/<int:eid>/rsvp", methods=["POST"])
    @approved_required
    def rsvp(eid):
        if not query("SELECT 1 FROM events WHERE id=?", (eid,), one=True):
            abort(404)
        uid = current_user()["id"]
        if query("SELECT 1 FROM rsvps WHERE event_id=? AND user_id=?", (eid, uid), one=True):
            execute("DELETE FROM rsvps WHERE event_id=? AND user_id=?", (eid, uid))
            flash("You are no longer marked as attending.", "info")
        else:
            execute("INSERT INTO rsvps (event_id, user_id) VALUES (?,?)", (eid, uid))
            flash("See you there! You're marked as attending.", "success")
        return redirect(safe_next(request.form.get("next")) or url_for("event_detail", eid=eid))

    @app.route("/events/<int:eid>/delete", methods=["POST"])
    @admin_required
    def delete_event(eid):
        execute("DELETE FROM events WHERE id=?", (eid,))
        flash("Event deleted.", "info")
        return redirect(url_for("events"))

    # ---- jobs

    @app.route("/jobs")
    @approved_required
    def jobs():
        job_type = request.args.get("type", "")
        sql = "SELECT j.*, u.name poster, u.batch_year poster_batch FROM jobs j JOIN users u ON u.id=j.posted_by WHERE is_open=1"
        args = []
        if job_type in JOB_TYPES:
            sql += " AND job_type=?"
            args.append(job_type)
        listings = query(sql + " ORDER BY j.created_at DESC, j.id DESC", args)
        mine = query("SELECT * FROM jobs WHERE posted_by=? AND is_open=0 ORDER BY created_at DESC", (current_user()["id"],))
        return render_template("jobs.html", jobs=listings, closed_mine=mine, job_types=JOB_TYPES, job_type=job_type)

    @app.route("/jobs/new", methods=["GET", "POST"])
    @approved_required
    def new_job():
        v = {}
        if request.method == "POST":
            v = {k: form(k) for k in ("title", "company", "location", "job_type", "description", "apply_link")}
            v["apply_link"] = safe_url(v["apply_link"])
            if not (v["title"] and v["company"] and v["description"]):
                flash("Title, company and description are required.", "error")
            elif v["job_type"] not in JOB_TYPES:
                flash("Please choose a job type.", "error")
            else:
                execute("""INSERT INTO jobs (title, company, location, job_type, description, apply_link, posted_by)
                           VALUES (?,?,?,?,?,?,?)""",
                        (v["title"], v["company"], v["location"], v["job_type"], v["description"],
                         v["apply_link"], current_user()["id"]))
                notify_new_post("job", f"{v['title']} at {v['company']}", f"{v['job_type']}\n{v['description']}",
                                "/jobs", current_user()["id"])
                flash("Opportunity posted. Thanks for helping fellow alumni!", "success")
                return redirect(url_for("jobs"))
        return render_template("job_form.html", v=v, job_types=JOB_TYPES)

    @app.route("/jobs/<int:jid>/<action>", methods=["POST"])
    @approved_required
    def job_action(jid, action):
        job = query("SELECT * FROM jobs WHERE id=?", (jid,), one=True)
        if not job:
            abort(404)
        if job["posted_by"] != current_user()["id"] and current_user()["role"] != "admin":
            abort(403)
        if action == "close":
            execute("UPDATE jobs SET is_open=0 WHERE id=?", (jid,))
            flash("Listing closed.", "info")
        elif action == "reopen":
            execute("UPDATE jobs SET is_open=1 WHERE id=?", (jid,))
            flash("Listing reopened.", "success")
        elif action == "delete":
            execute("DELETE FROM jobs WHERE id=?", (jid,))
            flash("Listing deleted.", "info")
        else:
            abort(404)
        return redirect(url_for("jobs"))

    # ---- news

    @app.route("/news")
    def news():
        items = query("""SELECT a.*, u.name author FROM announcements a LEFT JOIN users u ON u.id=a.posted_by
                         ORDER BY a.created_at DESC, a.id DESC""")
        return render_template("news.html", items=items)

    @app.route("/news/new", methods=["POST"])
    @admin_required
    def new_news():
        title, body = form("title"), form("body")
        if not (title and body):
            flash("Title and message are required.", "error")
        else:
            execute("INSERT INTO announcements (title, body, posted_by) VALUES (?,?,?)", (title, body, current_user()["id"]))
            notify_new_post("news", title, body, "/news", current_user()["id"])
            flash("Announcement posted.", "success")
        return redirect(url_for("news"))

    @app.route("/news/<int:nid>/delete", methods=["POST"])
    @admin_required
    def delete_news(nid):
        execute("DELETE FROM announcements WHERE id=?", (nid,))
        flash("Announcement deleted.", "info")
        return redirect(url_for("news"))

    # ---- memories wall

    @app.route("/memories", methods=["GET", "POST"])
    @approved_required
    def memories():
        if request.method == "POST":
            body = form("body")
            if len(body) < 5:
                flash("Share a little more — at least a few words.", "error")
            else:
                execute("INSERT INTO memories (user_id, body) VALUES (?,?)", (current_user()["id"], body[:2000]))
                flash("Memory added to the wall.", "success")
            return redirect(url_for("memories"))
        items = query("""SELECT m.*, u.name, u.batch_year, u.photo FROM memories m JOIN users u ON u.id=m.user_id
                         ORDER BY m.created_at DESC, m.id DESC LIMIT 100""")
        return render_template("memories.html", items=items)

    @app.route("/memories/<int:mid>/delete", methods=["POST"])
    @approved_required
    def delete_memory(mid):
        m = query("SELECT * FROM memories WHERE id=?", (mid,), one=True)
        if not m:
            abort(404)
        if m["user_id"] != current_user()["id"] and current_user()["role"] != "admin":
            abort(403)
        execute("DELETE FROM memories WHERE id=?", (mid,))
        flash("Memory removed.", "info")
        return redirect(url_for("memories"))

    # ---- admin

    @app.route("/admin")
    @admin_required
    def admin():
        status = request.args.get("status", "pending")
        if status not in ("pending", "approved", "rejected", "suspended", "all"):
            status = "pending"
        if status == "all":
            users = query("SELECT * FROM users ORDER BY created_at DESC")
        else:
            users = query("SELECT * FROM users WHERE status=? ORDER BY created_at DESC", (status,))
        counts = {r["status"]: r["c"] for r in query("SELECT status, COUNT(*) c FROM users GROUP BY status")}
        by_batch = query("""SELECT batch_year, COUNT(*) c FROM users WHERE status='approved'
                            GROUP BY batch_year ORDER BY batch_year DESC LIMIT 12""")
        totals = {
            "events": query("SELECT COUNT(*) c FROM events", one=True)["c"],
            "jobs": query("SELECT COUNT(*) c FROM jobs WHERE is_open=1", one=True)["c"],
            "memories": query("SELECT COUNT(*) c FROM memories", one=True)["c"],
        }
        return render_template("admin.html", users=users, status=status, counts=counts,
                               by_batch=by_batch, totals=totals)

    @app.route("/admin/users/<int:uid>/<action>", methods=["POST"])
    @admin_required
    def admin_user_action(uid, action):
        target = query("SELECT * FROM users WHERE id=?", (uid,), one=True)
        if not target:
            abort(404)
        if target["id"] == current_user()["id"]:
            flash("You cannot change your own account from here.", "error")
            return redirect(url_for("admin"))
        updates = {
            "approve": ("status", "approved"), "reject": ("status", "rejected"),
            "suspend": ("status", "suspended"), "restore": ("status", "approved"),
            "make_admin": ("role", "admin"), "remove_admin": ("role", "alumni"),
        }
        if action == "delete":
            execute("DELETE FROM users WHERE id=?", (uid,))
            flash(f"Deleted {target['name']}.", "info")
        elif action in updates:
            col, val = updates[action]
            execute(f"UPDATE users SET {col}=? WHERE id=?", (val, uid))
            flash(f"{target['name']}: {action.replace('_', ' ')} done.", "success")
        else:
            abort(404)
        return redirect(safe_next(request.form.get("next")) or url_for("admin"))

    # ---- errors (JSON for /api, HTML pages otherwise)

    def error_page(code, message):
        if request.path.startswith("/api/"):
            return jsonify(error=message), code
        return render_template("error.html", code=code, message=message), code

    @app.errorhandler(400)
    def bad_request(e):
        return error_page(400, e.description)

    @app.errorhandler(401)
    def unauthorized(_e):
        return error_page(401, "Please sign in to continue.")

    @app.errorhandler(403)
    def forbidden(_e):
        return error_page(403, "You don't have permission to view this page.")

    @app.errorhandler(404)
    def not_found(_e):
        return error_page(404, "We couldn't find that page.")

    @app.errorhandler(405)
    def not_allowed(_e):
        return error_page(405, "That action isn't allowed here.")

    @app.errorhandler(413)
    def too_large(_e):
        return error_page(413, "That file is too large. Photos must be under 3 MB.")

app = create_app()

if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5000)),
            debug=os.environ.get("FLASK_DEBUG") == "1")
