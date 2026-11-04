"""
Management commands.

  python manage.py create-admin             create (or promote) an admin account
  python manage.py seed-demo                add sample events, news and jobs
"""

import argparse
import getpass
import sys
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from app import app, validate_password
from db import execute, query


def create_admin(args):
    email = (args.email or input("Admin email: ")).strip().lower()
    name = (args.name or input("Full name: ")).strip()
    password = getpass.getpass("Password: ")
    problem = validate_password(password)
    if problem:
        sys.exit(problem)
    if password != getpass.getpass("Confirm password: "):
        sys.exit("Passwords do not match.")
    existing = query("SELECT id FROM users WHERE email=?", (email,), one=True)
    if existing:
        execute("UPDATE users SET role='admin', status='approved', password_hash=? WHERE id=?",
                (generate_password_hash(password), existing["id"]))
        print(f"Promoted existing account {email} to admin.")
    else:
        execute("""INSERT INTO users (name, email, password_hash, batch_year, last_class, role, status)
                   VALUES (?,?,?,?, 'XII', 'admin', 'approved')""",
                (name or "Portal Admin", email, generate_password_hash(password), datetime.now().year))
        print(f"Created admin account {email}.")


def seed_demo(_args):
    admin = query("SELECT id FROM users WHERE role='admin' LIMIT 1", one=True)
    if not admin:
        sys.exit("Create an admin first:  python manage.py create-admin")
    aid = admin["id"]
    soon = datetime.now() + timedelta(days=21)
    later = datetime.now() + timedelta(days=60)
    execute("INSERT INTO events (title, description, location, starts_at, created_by) VALUES (?,?,?,?,?)",
            ("Annual Alumni Meet", "Reconnect with batchmates and teachers. Campus tour, cultural programme and lunch.",
             "School Auditorium, Kalapet", soon.strftime("%Y-%m-%dT10:00"), aid))
    execute("INSERT INTO events (title, description, location, starts_at, created_by) VALUES (?,?,?,?,?)",
            ("Career Guidance Session for Class XII", "Alumni volunteers share their journeys in engineering, medicine, "
             "civil services, design and business. Mentors please RSVP.", "Library Hall", later.strftime("%Y-%m-%dT14:30"), aid))
    execute("INSERT INTO announcements (title, body, posted_by) VALUES (?,?,?)",
            ("Welcome to the new Alumni Portal",
             "We are delighted to launch the official alumni portal. Create your profile, find your batchmates and "
             "help us build a strong alumni network for current students.", aid))
    execute("INSERT INTO jobs (title, company, location, job_type, description, apply_link, posted_by) VALUES (?,?,?,?,?,?,?)",
            ("Summer Intern - Web Development", "Example Tech Pvt Ltd", "Chennai / Remote", "Internship",
             "Looking for students or recent graduates comfortable with HTML, CSS and Python.", "", aid))
    print("Demo events, announcement and job added.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("create-admin")
    p.add_argument("--email")
    p.add_argument("--name")
    p.set_defaults(func=create_admin)
    sub.add_parser("seed-demo").set_defaults(func=seed_demo)
    args = parser.parse_args()
    with app.app_context():
        args.func(args)


if __name__ == "__main__":
    main()
