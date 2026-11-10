"""JSON API used by the Next.js frontend (web/). Auth is the same Flask session cookie as the HTML pages."""

import hashlib
import os
import secrets
import time
from datetime import datetime
from functools import wraps

from flask import Blueprint, abort, current_app, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from core import (CLASSES, EMAIL_RE, JOB_TYPES, PUBLIC_USER_FIELDS, SCHOOL, STREAMS, _failed_logins, csrf_token,
                  is_locked, profile_fields_from, safe_url, save_photo, validate_password, validate_profile)
from db import execute, query, requires_approval

bp = Blueprint("api", __name__, url_prefix="/api")


def now_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M")


def body():
    return request.get_json(silent=True) or {}


def fail(message, code=400):
    return jsonify(error=message), code


def user_json(row, private=False):
    if row is None:
        return None
    me = g.get("user")
    data = {k: row[k] for k in PUBLIC_USER_FIELDS}
    data["photo_url"] = f"/uploads/{row['photo']}" if row["photo"] else None
    can_see_contact = private or row["show_contact"] or (me and (me["id"] == row["id"] or me["role"] == "admin"))
    if can_see_contact:
        data.update(email=row["email"], phone=row["phone"])
    if private:
        data.update(status=row["status"], show_contact=row["show_contact"], admission_no=row["admission_no"])
    return data


def rows(result):
    return [dict(r) for r in result]


def api_login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not g.get("user"):
            abort(401)
        return view(*a, **kw)
    return wrapped


def api_approved_required(view):
    @wraps(view)
    @api_login_required
    def wrapped(*a, **kw):
        if g.user["status"] != "approved":
            return fail("Your account is still waiting for verification.", 403)
        return view(*a, **kw)
    return wrapped


def api_admin_required(view):
    @wraps(view)
    @api_login_required
    def wrapped(*a, **kw):
        if g.user["role"] != "admin":
            abort(403)
        return view(*a, **kw)
    return wrapped


# ---------------------------------------------------------------- session

@bp.get("/me")
def me():
    user = user_json(g.user, private=True) if g.user else None
    if user and user["role"] == "admin":
        user["pending_count"] = query("SELECT COUNT(*) c FROM users WHERE status='pending'", one=True)["c"]
    return jsonify(user=user, csrf=csrf_token(),
                   school=SCHOOL, options={"streams": STREAMS, "classes": CLASSES, "job_types": JOB_TYPES},
                   require_approval=requires_approval())


@bp.post("/auth/signup")
def signup():
    if g.user:
        return fail("You are already signed in.")
    data = body()
    values = profile_fields_from(data)
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    error = validate_profile(values)
    if not error and not EMAIL_RE.match(email):
        error = "Please enter a valid email address."
    if not error:
        error = validate_password(password)
    if not error and not data.get("agree"):
        error = "Please confirm that you studied at the school."
    if not error and query("SELECT 1 FROM users WHERE email = ?", (email,), one=True):
        error = "An account with this email already exists. Sign in instead."
    if error:
        return fail(error)
    status = "pending" if requires_approval() else "approved"
    uid = execute(
        """INSERT INTO users (name, email, password_hash, phone, batch_year, last_class, stream, house,
            admission_no, city, country, occupation, organization, industry, linkedin, bio,
            willing_to_mentor, show_contact, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (values["name"], email, generate_password_hash(password), values["phone"], int(values["batch_year"]),
         values["last_class"], values["stream"], values["house"], values["admission_no"], values["city"],
         values["country"], values["occupation"], values["organization"], values["industry"],
         values["linkedin"], values["bio"], values["willing_to_mentor"], values["show_contact"], status))
    session.clear()
    session["uid"] = uid
    session["csrf"] = os.urandom(24).hex()
    session.permanent = True
    user = query("SELECT * FROM users WHERE id=?", (uid,), one=True)
    return jsonify(user=user_json(user, private=True), csrf=session["csrf"]), 201


@bp.post("/auth/login")
def login():
    data = body()
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    key = f"{request.remote_addr}|{email}"
    if is_locked(key):
        return fail("Too many failed attempts. Wait 10 minutes, then try again.", 429)
    user = query("SELECT * FROM users WHERE email = ?", (email,), one=True)
    if not user or not check_password_hash(user["password_hash"], password):
        _failed_logins[key].append(time.time())
        return fail("That email and password don't match. Check them and try again.", 401)
    if user["status"] == "suspended":
        return fail("This account is suspended. Contact the school's alumni coordinator.", 403)
    if user["status"] == "rejected":
        return fail("Your registration wasn't approved. Contact the school's alumni coordinator.", 403)
    _failed_logins.pop(key, None)
    session.clear()
    session["uid"] = user["id"]
    session["csrf"] = os.urandom(24).hex()
    session.permanent = bool(data.get("remember"))
    execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user["id"],))
    return jsonify(user=user_json(user, private=True), csrf=session["csrf"])


@bp.post("/auth/logout")
def logout():
    session.clear()
    session["csrf"] = os.urandom(24).hex()
    return jsonify(ok=True, csrf=session["csrf"])


# ---------------------------------------------------------------- public

@bp.get("/home")
def home():
    now = now_iso()
    stats = {
        "alumni": query("SELECT COUNT(*) c FROM users WHERE status='approved'", one=True)["c"],
        "batches": query("SELECT COUNT(DISTINCT batch_year) c FROM users WHERE status='approved'", one=True)["c"],
        "mentors": query("SELECT COUNT(*) c FROM users WHERE status='approved' AND willing_to_mentor=1", one=True)["c"],
        "events": query("SELECT COUNT(*) c FROM events WHERE starts_at >= ?", (now,), one=True)["c"],
    }
    news = rows(query("SELECT id, title, body, created_at FROM announcements ORDER BY created_at DESC, id DESC LIMIT 3"))
    events = rows(query("SELECT id, title, location, starts_at FROM events WHERE starts_at >= ? ORDER BY starts_at LIMIT 3", (now,)))
    return jsonify(stats=stats, news=news, events=events)


@bp.get("/news")
def news():
    items = rows(query("""SELECT a.*, u.name author FROM announcements a LEFT JOIN users u ON u.id=a.posted_by
                          ORDER BY a.created_at DESC, a.id DESC"""))
    return jsonify(items=items)


# ---------------------------------------------------------------- members

EVENT_SQL = """SELECT e.*, (SELECT COUNT(*) FROM rsvps r WHERE r.event_id=e.id) going,
                      EXISTS(SELECT 1 FROM rsvps r WHERE r.event_id=e.id AND r.user_id=?) mine
               FROM events e"""


@bp.get("/dashboard")
@api_approved_required
def dashboard():
    u = g.user
    batchmates = [user_json(r) for r in query(
        "SELECT * FROM users WHERE status='approved' AND batch_year=? AND id<>? ORDER BY name LIMIT 8",
        (u["batch_year"], u["id"]))]
    events = rows(query(EVENT_SQL + " WHERE starts_at >= ? ORDER BY starts_at LIMIT 3", (u["id"], now_iso())))
    news_items = rows(query("SELECT * FROM announcements ORDER BY created_at DESC, id DESC LIMIT 3"))
    jobs = rows(query("""SELECT j.*, u.name poster FROM jobs j JOIN users u ON u.id=j.posted_by
                         WHERE is_open=1 ORDER BY j.created_at DESC, j.id DESC LIMIT 4"""))
    fields = ("phone", "city", "occupation", "organization", "bio", "photo", "stream", "linkedin")
    completeness = int(sum(1 for f in fields if u[f]) / len(fields) * 100)
    return jsonify(batchmates=batchmates, events=events, news=news_items, jobs=jobs, completeness=completeness)


@bp.get("/directory")
@api_approved_required
def directory():
    q, batch, city = (request.args.get(k, "").strip() for k in ("q", "batch", "city"))
    sql, args = "SELECT * FROM users WHERE status='approved'", []
    if q:
        sql += " AND (name LIKE ? OR occupation LIKE ? OR organization LIKE ? OR industry LIKE ?)"
        args += [f"%{q}%"] * 4
    if batch.isdigit():
        sql += " AND batch_year = ?"
        args.append(int(batch))
    if city:
        sql += " AND city LIKE ?"
        args.append(f"%{city}%")
    if request.args.get("mentor") == "1":
        sql += " AND willing_to_mentor = 1"
    people = [user_json(r) for r in query(sql + " ORDER BY batch_year DESC, name LIMIT 300", args)]
    batches = [r["batch_year"] for r in query(
        "SELECT DISTINCT batch_year FROM users WHERE status='approved' ORDER BY batch_year DESC")]
    return jsonify(people=people, batches=batches)


@bp.get("/alumni/<int:uid>")
@api_approved_required
def alumni(uid):
    person = query("SELECT * FROM users WHERE id=? AND status='approved'", (uid,), one=True)
    if not person:
        abort(404)
    memories = rows(query("SELECT * FROM memories WHERE user_id=? ORDER BY created_at DESC LIMIT 5", (uid,)))
    jobs = rows(query("SELECT * FROM jobs WHERE posted_by=? AND is_open=1 ORDER BY created_at DESC", (uid,)))
    return jsonify(person=user_json(person), memories=memories, jobs=jobs)


@bp.put("/profile")
@api_login_required
def update_profile():
    values = profile_fields_from(body())
    error = validate_profile(values)
    if error:
        return fail(error)
    values["batch_year"] = int(values["batch_year"])
    sets = ", ".join(f"{c}=?" for c in values)
    execute(f"UPDATE users SET {sets} WHERE id=?", (*values.values(), g.user["id"]))
    user = query("SELECT * FROM users WHERE id=?", (g.user["id"],), one=True)
    return jsonify(user=user_json(user, private=True))


@bp.post("/profile/photo")
@api_login_required
def upload_photo():
    folder = current_app.config["UPLOAD_FOLDER"]
    photo, error = save_photo(request.files.get("photo"), folder)
    if error or not photo:
        return fail(error or "Choose a photo to upload.")
    old = g.user["photo"]
    execute("UPDATE users SET photo=? WHERE id=?", (photo, g.user["id"]))
    if old and os.path.exists(os.path.join(folder, old)):
        os.remove(os.path.join(folder, old))
    return jsonify(photo_url=f"/uploads/{photo}")


@bp.post("/password")
@api_login_required
def change_password():
    data = body()
    new = str(data.get("new_password") or "")
    if not check_password_hash(g.user["password_hash"], str(data.get("current_password") or "")):
        return fail("Your current password is incorrect.")
    error = validate_password(new)
    if error:
        return fail(error)
    execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(new), g.user["id"]))
    return jsonify(ok=True)


# ---------------------------------------------------------------- events

@bp.get("/events")
@api_approved_required
def events():
    now, uid = now_iso(), g.user["id"]
    upcoming = rows(query(EVENT_SQL + " WHERE starts_at >= ? ORDER BY starts_at", (uid, now)))
    past = rows(query(EVENT_SQL + " WHERE starts_at < ? ORDER BY starts_at DESC LIMIT 10", (uid, now)))
    return jsonify(upcoming=upcoming, past=past)


@bp.post("/events")
@api_admin_required
def create_event():
    data = body()
    v = {k: str(data.get(k) or "").strip() for k in ("title", "description", "location", "starts_at")}
    if not all(v.values()):
        return fail("Fill in the title, date, venue and description.")
    try:
        datetime.fromisoformat(v["starts_at"])
    except ValueError:
        return fail("Pick a valid date and time.")
    eid = execute("INSERT INTO events (title, description, location, starts_at, created_by) VALUES (?,?,?,?,?)",
                  (v["title"], v["description"], v["location"], v["starts_at"][:16], g.user["id"]))
    return jsonify(id=eid), 201


@bp.get("/events/<int:eid>")
@api_approved_required
def event_detail(eid):
    event = query(EVENT_SQL + " WHERE id=?", (g.user["id"], eid), one=True)
    if not event:
        abort(404)
    attendees = [user_json(r) for r in query(
        "SELECT u.* FROM rsvps r JOIN users u ON u.id=r.user_id WHERE r.event_id=? ORDER BY r.created_at", (eid,))]
    return jsonify(event=dict(event), attendees=attendees, is_past=event["starts_at"] < now_iso())


@bp.post("/events/<int:eid>/rsvp")
@api_approved_required
def rsvp(eid):
    if not query("SELECT 1 FROM events WHERE id=?", (eid,), one=True):
        abort(404)
    uid = g.user["id"]
    if query("SELECT 1 FROM rsvps WHERE event_id=? AND user_id=?", (eid, uid), one=True):
        execute("DELETE FROM rsvps WHERE event_id=? AND user_id=?", (eid, uid))
        going = False
    else:
        execute("INSERT INTO rsvps (event_id, user_id) VALUES (?,?)", (eid, uid))
        going = True
    count = query("SELECT COUNT(*) c FROM rsvps WHERE event_id=?", (eid,), one=True)["c"]
    return jsonify(mine=going, going=count)


@bp.delete("/events/<int:eid>")
@api_admin_required
def delete_event(eid):
    execute("DELETE FROM events WHERE id=?", (eid,))
    return jsonify(ok=True)


# ---------------------------------------------------------------- jobs

@bp.get("/jobs")
@api_approved_required
def jobs():
    sql = """SELECT j.*, u.name poster, u.batch_year poster_batch FROM jobs j
             JOIN users u ON u.id=j.posted_by WHERE is_open=1"""
    args = []
    if request.args.get("type") in JOB_TYPES:
        sql += " AND job_type=?"
        args.append(request.args["type"])
    listings = rows(query(sql + " ORDER BY j.created_at DESC, j.id DESC", args))
    closed = rows(query("SELECT * FROM jobs WHERE posted_by=? AND is_open=0 ORDER BY created_at DESC", (g.user["id"],)))
    return jsonify(jobs=listings, closed_mine=closed)


@bp.post("/jobs")
@api_approved_required
def create_job():
    data = body()
    v = {k: str(data.get(k) or "").strip() for k in ("title", "company", "location", "job_type", "description", "apply_link")}
    v["apply_link"] = safe_url(v["apply_link"])
    if not (v["title"] and v["company"] and v["description"]):
        return fail("Add a role, organisation and description.")
    if v["job_type"] not in JOB_TYPES:
        return fail("Choose a job type.")
    jid = execute("""INSERT INTO jobs (title, company, location, job_type, description, apply_link, posted_by)
                     VALUES (?,?,?,?,?,?,?)""",
                  (v["title"], v["company"], v["location"], v["job_type"], v["description"], v["apply_link"], g.user["id"]))
    return jsonify(id=jid), 201


@bp.post("/jobs/<int:jid>/<action>")
@api_approved_required
def job_action(jid, action):
    job = query("SELECT * FROM jobs WHERE id=?", (jid,), one=True)
    if not job:
        abort(404)
    if job["posted_by"] != g.user["id"] and g.user["role"] != "admin":
        abort(403)
    if action == "close":
        execute("UPDATE jobs SET is_open=0 WHERE id=?", (jid,))
    elif action == "reopen":
        execute("UPDATE jobs SET is_open=1 WHERE id=?", (jid,))
    elif action == "delete":
        execute("DELETE FROM jobs WHERE id=?", (jid,))
    else:
        abort(404)
    return jsonify(ok=True)


# ---------------------------------------------------------------- news (admin writes)

@bp.post("/news")
@api_admin_required
def create_news():
    data = body()
    title, text = str(data.get("title") or "").strip(), str(data.get("body") or "").strip()
    if not (title and text):
        return fail("Add a title and a message.")
    nid = execute("INSERT INTO announcements (title, body, posted_by) VALUES (?,?,?)", (title, text, g.user["id"]))
    return jsonify(id=nid), 201


@bp.delete("/news/<int:nid>")
@api_admin_required
def delete_news(nid):
    execute("DELETE FROM announcements WHERE id=?", (nid,))
    return jsonify(ok=True)


# ---------------------------------------------------------------- memories

@bp.get("/memories")
@api_approved_required
def memories():
    items = rows(query("""SELECT m.*, u.name, u.batch_year, u.photo FROM memories m JOIN users u ON u.id=m.user_id
                          ORDER BY m.created_at DESC, m.id DESC LIMIT 100"""))
    for m in items:
        m["photo_url"] = f"/uploads/{m['photo']}" if m["photo"] else None
    return jsonify(items=items)


@bp.post("/memories")
@api_approved_required
def create_memory():
    text = str(body().get("body") or "").strip()
    if len(text) < 5:
        return fail("Write a little more, at least a few words.")
    mid = execute("INSERT INTO memories (user_id, body) VALUES (?,?)", (g.user["id"], text[:2000]))
    return jsonify(id=mid), 201


@bp.delete("/memories/<int:mid>")
@api_approved_required
def delete_memory(mid):
    m = query("SELECT * FROM memories WHERE id=?", (mid,), one=True)
    if not m:
        abort(404)
    if m["user_id"] != g.user["id"] and g.user["role"] != "admin":
        abort(403)
    execute("DELETE FROM memories WHERE id=?", (mid,))
    return jsonify(ok=True)


# ---------------------------------------------------------------- admin

@bp.get("/admin")
@api_admin_required
def admin():
    status = request.args.get("status", "pending")
    if status not in ("pending", "approved", "rejected", "suspended", "all"):
        status = "pending"
    if status == "all":
        users = query("SELECT * FROM users ORDER BY created_at DESC")
    else:
        users = query("SELECT * FROM users WHERE status=? ORDER BY created_at DESC", (status,))
    counts = {r["status"]: r["c"] for r in query("SELECT status, COUNT(*) c FROM users GROUP BY status")}
    by_batch = rows(query("""SELECT batch_year, COUNT(*) c FROM users WHERE status='approved'
                             GROUP BY batch_year ORDER BY batch_year DESC LIMIT 12"""))
    totals = {
        "events": query("SELECT COUNT(*) c FROM events", one=True)["c"],
        "jobs": query("SELECT COUNT(*) c FROM jobs WHERE is_open=1", one=True)["c"],
        "memories": query("SELECT COUNT(*) c FROM memories", one=True)["c"],
    }
    users_out = [{**user_json(u, private=True), "created_at": u["created_at"]} for u in users]
    return jsonify(users=users_out, counts=counts, by_batch=by_batch, totals=totals,
                   settings={"auto_approve": not requires_approval()})


@bp.post("/admin/settings")
@api_admin_required
def update_settings():
    data = body()
    if "auto_approve" not in data:
        return fail("Nothing to change.")
    value = "1" if data["auto_approve"] in (True, 1, "1", "true") else "0"
    execute("INSERT INTO settings (key, value) VALUES ('auto_approve', ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (value,))
    return jsonify(settings={"auto_approve": value == "1"})


@bp.post("/admin/approve-pending")
@api_admin_required
def approve_all_pending():
    count = query("SELECT COUNT(*) c FROM users WHERE status='pending'", one=True)["c"]
    execute("UPDATE users SET status='approved' WHERE status='pending'")
    return jsonify(approved=count)


@bp.post("/admin/users/<int:uid>/<action>")
@api_admin_required
def admin_user_action(uid, action):
    target = query("SELECT * FROM users WHERE id=?", (uid,), one=True)
    if not target:
        abort(404)
    if target["id"] == g.user["id"]:
        return fail("You can't change your own account here.")
    updates = {
        "approve": ("status", "approved"), "reject": ("status", "rejected"),
        "suspend": ("status", "suspended"), "restore": ("status", "approved"),
        "make_admin": ("role", "admin"), "remove_admin": ("role", "alumni"),
    }
    if action == "delete":
        execute("DELETE FROM users WHERE id=?", (uid,))
    elif action in updates:
        col, val = updates[action]
        execute(f"UPDATE users SET {col}=? WHERE id=?", (val, uid))
    else:
        abort(404)
    return jsonify(ok=True)


# ---------------------------------------------------------------- password reset (coordinator-issued links)

RESET_HOURS = 24


def _reset_row(token):
    token_hash = hashlib.sha256(str(token or "").encode()).hexdigest()
    return query("""SELECT r.*, u.name, u.status FROM password_resets r JOIN users u ON u.id=r.user_id
                    WHERE r.token_hash=? AND r.expires_at > datetime('now')""", (token_hash,), one=True)


@bp.post("/admin/users/<int:uid>/reset-link")
@api_admin_required
def create_reset_link(uid):
    target = query("SELECT * FROM users WHERE id=?", (uid,), one=True)
    if not target:
        abort(404)
    token = secrets.token_urlsafe(32)
    execute("DELETE FROM password_resets WHERE user_id=?", (uid,))  # only the newest link works
    execute("""INSERT INTO password_resets (token_hash, user_id, created_by, expires_at)
               VALUES (?, ?, ?, datetime('now', ?))""",
            (hashlib.sha256(token.encode()).hexdigest(), uid, g.user["id"], f"+{RESET_HOURS} hours"))
    return jsonify(path=f"/reset-password?token={token}", hours=RESET_HOURS, name=target["name"])


@bp.get("/auth/reset-password")
def check_reset_link():
    row = _reset_row(request.args.get("token"))
    if not row:
        return fail("This reset link is invalid or has expired. Ask the alumni coordinator for a new one.", 404)
    return jsonify(name=row["name"].split()[0], expires_at=row["expires_at"])


@bp.post("/auth/reset-password")
def reset_password():
    data = body()
    row = _reset_row(data.get("token"))
    if not row:
        return fail("This reset link is invalid or has expired. Ask the alumni coordinator for a new one.", 404)
    new = str(data.get("new_password") or "")
    error = validate_password(new)
    if error:
        return fail(error)
    execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(new), row["user_id"]))
    execute("DELETE FROM password_resets WHERE user_id=?", (row["user_id"],))  # links are single-use
    user = query("SELECT email FROM users WHERE id=?", (row["user_id"],), one=True)
    for key in [k for k in _failed_logins if k.endswith("|" + user["email"])]:
        _failed_logins.pop(key, None)  # a fresh password shouldn't stay locked out
    return jsonify(ok=True)
