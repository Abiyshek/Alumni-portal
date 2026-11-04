"""End-to-end tests using Flask's test client.  Run:  python -m unittest discover tests"""

import io
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash  # noqa: E402

import app as portal  # noqa: E402

TEST_PW = "Test1234pass"


class PortalTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        portal._failed_logins.clear()
        self.app = portal.create_app({
            "TESTING": True,
            "DATABASE": os.path.join(self.tmp, "test.db"),
            "UPLOAD_FOLDER": os.path.join(self.tmp, "uploads"),
            "REQUIRE_APPROVAL": True,
        })
        conn = sqlite3.connect(self.app.config["DATABASE"])
        conn.execute("""INSERT INTO users (name, email, password_hash, batch_year, role, status)
                        VALUES ('Admin User', 'admin@test.local', ?, 2000, 'admin', 'approved')""",
                     (generate_password_hash(TEST_PW),))
        conn.commit()
        conn.close()
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # helpers
    def csrf(self, client=None):
        client = client or self.client
        client.get("/")
        with client.session_transaction() as s:
            return s["csrf"]

    def post(self, url, data=None, client=None, **kw):
        client = client or self.client
        data = dict(data or {})
        data["csrf_token"] = self.csrf(client)
        return client.post(url, data=data, **kw)

    def signup(self, client, email="ravi@test.local", name="Ravi Kumar", batch="2015", **extra):
        data = {"name": name, "email": email, "password": TEST_PW, "confirm_password": TEST_PW,
                "batch_year": batch, "last_class": "XII", "stream": "Science", "city": "Chennai",
                "agree": "1", **extra}
        return self.post("/signup", data, client=client, follow_redirects=True)

    def login(self, client, email, pw=TEST_PW):
        return self.post("/login", {"email": email, "password": pw}, client=client, follow_redirects=True)

    def user_row(self, email):
        conn = sqlite3.connect(self.app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        return row

    # tests
    def test_public_pages(self):
        for url in ("/", "/login", "/signup", "/news"):
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get("/nope").status_code, 404)

    def test_members_pages_require_login(self):
        for url in ("/dashboard", "/directory", "/events", "/jobs", "/memories", "/admin"):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertIn("/login", r.headers["Location"])

    def test_signup_stores_hashed_password_and_is_pending(self):
        r = self.signup(self.client)
        self.assertIn(b"waiting for verification", r.data)
        row = self.user_row("ravi@test.local")
        self.assertEqual(row["status"], "pending")
        self.assertNotEqual(row["password_hash"], TEST_PW)
        self.assertTrue(row["password_hash"].startswith(("scrypt:", "pbkdf2:")))
        # pending users can't see the directory
        r = self.client.get("/directory")
        self.assertIn("/pending", r.headers["Location"])

    def test_signup_validation(self):
        self.signup(self.client)
        other = self.app.test_client()
        r = self.signup(other)  # duplicate
        self.assertIn(b"already exists", r.data)
        r = self.post("/signup", {"name": "X Y", "email": "x@test.local", "password": "short",
                                  "confirm_password": "short", "batch_year": "2010", "last_class": "XII",
                                  "agree": "1"}, client=other)
        self.assertIn(b"at least 8 characters", r.data)
        r = self.post("/signup", {"name": "X Y", "email": "x@test.local", "password": TEST_PW,
                                  "confirm_password": TEST_PW, "batch_year": "1950", "last_class": "XII",
                                  "agree": "1"}, client=other)
        self.assertIn(b"Batch year must be", r.data)

    def test_csrf_required(self):
        r = self.client.post("/login", data={"email": "admin@test.local", "password": TEST_PW})
        self.assertEqual(r.status_code, 400)

    def test_login_logout_and_bad_password(self):
        r = self.login(self.client, "admin@test.local", "wrong-password1")
        self.assertIn(b"Incorrect email or password", r.data)
        r = self.login(self.client, "ADMIN@test.local")  # email is case-insensitive
        self.assertIn(b"Welcome back", r.data)
        r = self.post("/logout", follow_redirects=True)
        self.assertIn(b"signed out", r.data)
        self.assertEqual(self.client.get("/dashboard").status_code, 302)

    def test_lockout_after_repeated_failures(self):
        for _ in range(5):
            self.login(self.client, "admin@test.local", "wrong-password1")
        r = self.login(self.client, "admin@test.local")
        self.assertIn(b"Too many failed attempts", r.data)

    def test_open_redirect_blocked(self):
        self.client.get("/")
        r = self.client.post("/login?next=//evil.example", data={
            "email": "admin@test.local", "password": TEST_PW, "csrf_token": self.csrf()})
        self.assertEqual(r.headers["Location"], "/dashboard")

    def test_full_alumni_flow(self):
        alum = self.app.test_client()
        self.signup(alum)
        uid = self.user_row("ravi@test.local")["id"]

        # non-admin cannot reach admin
        self.assertEqual(alum.get("/admin").status_code, 403)

        # admin approves
        self.login(self.client, "admin@test.local")
        r = self.client.get("/admin")
        self.assertIn(b"Ravi Kumar", r.data)
        self.post(f"/admin/users/{uid}/approve")
        self.assertEqual(self.user_row("ravi@test.local")["status"], "approved")

        # alumni now has access
        r = alum.get("/dashboard")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Hello, Ravi", r.data)

        # directory search
        r = alum.get("/directory?q=Ravi&batch=2015")
        self.assertIn(b"Ravi Kumar", r.data)
        r = alum.get("/directory?city=Mumbai")
        self.assertNotIn(b"Ravi Kumar", r.data)

        # admin creates an event; alumni RSVPs and cancels
        self.post("/events/new", {"title": "Alumni Meet", "description": "Reunion", "location": "Auditorium",
                                  "starts_at": "2099-01-10T10:00"})
        r = alum.get("/events")
        self.assertIn(b"Alumni Meet", r.data)
        self.assertEqual(self.post("/events/new", {"title": "x"}, client=alum).status_code, 403)
        self.post("/events/1/rsvp", client=alum)
        self.assertIn(b"Ravi Kumar", alum.get("/events/1").data)
        self.post("/events/1/rsvp", client=alum)
        self.assertNotIn(b"Batch 2015", alum.get("/events/1").data)

        # jobs: post, someone else can't delete, poster can close
        self.post("/jobs/new", {"title": "Intern", "company": "Acme", "job_type": "Internship",
                                "description": "Python intern", "apply_link": "acme.example/jobs"}, client=alum)
        r = alum.get("/jobs")
        self.assertIn(b"https://acme.example/jobs", r.data)
        third = self.app.test_client()
        self.signup(third, email="meena@test.local", name="Meena S", batch="2012")
        self.post(f"/admin/users/{self.user_row('meena@test.local')['id']}/approve")
        self.assertEqual(self.post("/jobs/1/delete", client=third).status_code, 403)
        self.post("/jobs/1/close", client=alum)
        self.assertIn(b"Your closed listings", alum.get("/jobs").data)

        # memories wall
        self.post("/memories", {"body": "Morning assembly in the rain!"}, client=alum)
        self.assertIn(b"Morning assembly", third.get("/memories").data)

        # profile edit + privacy of contact details
        self.post("/profile/edit", {"name": "Ravi Kumar", "batch_year": "2015", "last_class": "XII",
                                    "occupation": "Engineer", "organization": "ISRO", "show_contact": ""}, client=alum)
        r = third.get(f"/alumni/{uid}")
        self.assertIn(b"ISRO", r.data)
        self.assertNotIn(b"ravi@test.local", r.data)

        # suspend -> logged out and blocked
        self.post(f"/admin/users/{uid}/suspend")
        self.assertEqual(alum.get("/dashboard").status_code, 302)
        r = self.login(alum, "ravi@test.local")
        self.assertIn(b"suspended", r.data)

    def test_photo_upload_rejects_non_images(self):
        alum = self.app.test_client()
        self.signup(alum)
        base = {"name": "Ravi Kumar", "batch_year": "2015", "last_class": "XII"}
        r = self.post("/profile/edit", {**base, "photo": (io.BytesIO(b"<script>"), "x.png")},
                      client=alum, content_type="multipart/form-data")
        self.assertIn(b"does not look like a valid image", r.data)
        png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 50
        self.post("/profile/edit", {**base, "photo": (io.BytesIO(png), "me.png")},
                  client=alum, content_type="multipart/form-data")
        photo = self.user_row("ravi@test.local")["photo"]
        self.assertTrue(photo and photo.endswith(".png"))
        r = alum.get(f"/uploads/{photo}")
        self.assertEqual(r.status_code, 200)
        r.close()

    def test_change_password(self):
        self.login(self.client, "admin@test.local")
        r = self.post("/settings/password", {"current_password": "nope", "new_password": "NewPass123",
                                             "confirm_password": "NewPass123"}, follow_redirects=True)
        self.assertIn(b"current password is incorrect", r.data)
        r = self.post("/settings/password", {"current_password": TEST_PW, "new_password": "NewPass123",
                                             "confirm_password": "NewPass123"}, follow_redirects=True)
        self.assertIn(b"Password changed", r.data)
        self.post("/logout")
        self.assertIn(b"Welcome back", self.login(self.client, "admin@test.local", "NewPass123").data)


if __name__ == "__main__":
    unittest.main()
