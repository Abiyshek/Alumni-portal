"""Constants and validation helpers shared by the page routes (app.py) and the JSON API (api.py)."""

import os
import re
import secrets
import time
import uuid
from collections import defaultdict
from datetime import datetime

SCHOOL = {
    "name": "PM SHRI Kendriya Vidyalaya No. 2 Pondicherry",
    "short": "KV No. 2 Pondicherry",
    "location": "Kalapet, Puducherry",
    "established": 1986,
    "website": "https://no2pondicherry.kvs.ac.in/en/",
}

STREAMS = ["Science", "Commerce", "Humanities", "Not applicable"]
CLASSES = ["XII", "X", "Other"]
JOB_TYPES = ["Full-time", "Part-time", "Internship", "Contract", "Freelance"]
ALLOWED_PHOTO_EXT = {"png", "jpg", "jpeg", "webp"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Very small in-memory brute-force guard: key -> [failure timestamps]
_failed_logins = defaultdict(list)
MAX_FAILURES, LOCK_WINDOW = 5, 10 * 60

PUBLIC_USER_FIELDS = ("id", "name", "batch_year", "last_class", "stream", "house", "city", "country",
                      "occupation", "organization", "industry", "linkedin", "bio", "photo",
                      "willing_to_mentor", "role")


def csrf_token():
    """The session's CSRF token, created on first use.

    Only requests that hand a token out (HTML forms, /api/me) create one. If every request did, two parallel
    first-visit requests would each start a session, and the browser could keep one session's cookie while
    the page holds the other's token.
    """
    from flask import session  # local import: core stays importable without an app context
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def safe_next(target):
    # Only allow local redirects
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


def safe_url(link):
    link = (link or "").strip()
    if not link:
        return ""
    if not re.match(r"^https?://", link, re.I):
        link = "https://" + link
    return link


def validate_password(pw):
    if len(pw) < 8:
        return "Password must be at least 8 characters."
    if not (re.search(r"[A-Za-z]", pw) and re.search(r"\d", pw)):
        return "Password must contain both letters and numbers."
    return None


def save_photo(file_storage, upload_dir):
    if not file_storage or not file_storage.filename:
        return None, None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower() if "." in file_storage.filename else ""
    if ext not in ALLOWED_PHOTO_EXT:
        return None, "Photo must be a PNG, JPG or WEBP image."
    head = file_storage.stream.read(12)
    file_storage.stream.seek(0)
    is_image = (head.startswith(b"\x89PNG") or head.startswith(b"\xff\xd8\xff")
                or (head[:4] == b"RIFF" and head[8:12] == b"WEBP"))
    if not is_image:
        return None, "That file does not look like a valid image."
    name = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(upload_dir, name))
    return name, None


def is_locked(key):
    now = time.time()
    _failed_logins[key] = [t for t in _failed_logins[key] if now - t < LOCK_WINDOW]
    return len(_failed_logins[key]) >= MAX_FAILURES


def profile_fields_from(src):
    """Read profile fields from a form or JSON mapping."""
    def s(name, default=""):
        return str(src.get(name) or default).strip()

    def flag(name):
        return 1 if src.get(name) not in (None, "", False, 0, "0", "false") else 0

    return {
        "name": s("name"),
        "phone": s("phone"),
        "batch_year": s("batch_year"),
        "last_class": s("last_class", "XII"),
        "stream": s("stream"),
        "house": s("house"),
        "admission_no": s("admission_no"),
        "city": s("city"),
        "country": s("country", "India"),
        "occupation": s("occupation"),
        "organization": s("organization"),
        "industry": s("industry"),
        "linkedin": safe_url(s("linkedin")),
        "bio": s("bio")[:1000],
        "willing_to_mentor": flag("willing_to_mentor"),
        "show_contact": flag("show_contact"),
    }


def validate_profile(p):
    this_year = datetime.now().year
    if len(p["name"]) < 2:
        return "Please enter your full name."
    if not p["batch_year"].isdigit() or not (SCHOOL["established"] <= int(p["batch_year"]) <= this_year + 1):
        return f"Batch year must be between {SCHOOL['established']} and {this_year + 1}."
    if p["last_class"] not in CLASSES:
        return "Please choose the last class you studied at the school."
    if p["stream"] and p["stream"] not in STREAMS:
        return "Please choose a valid stream."
    if p["phone"] and not re.fullmatch(r"[0-9+\- ]{7,16}", p["phone"]):
        return "Please enter a valid phone number."
    return None
