"""Tests for the JSON API used by the Next.js frontend."""

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


class ApiClient:
    def __init__(self, flask_app):
        self.c = flask_app.test_client()
        self.csrf = self.c.get("/api/me").get_json()["csrf"]

    def get(self, url):
        return self.c.get(url)

    def send(self, method, url, json=None, **kw):
        r = getattr(self.c, method)(url, json=json, headers={"X-CSRF-Token": self.csrf}, **kw)
        data = r.get_json(silent=True) or {}
        if "csrf" in data:
            self.csrf = data["csrf"]
        return r

    def post(self, url, json=None, **kw):
        return self.send("post", url, json, **kw)


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        portal._failed_logins.clear()
        self.app = portal.create_app({"TESTING": True, "DATABASE": os.path.join(self.tmp, "t.db"),
                                      "UPLOAD_FOLDER": os.path.join(self.tmp, "up"), "REQUIRE_APPROVAL": True})
        conn = sqlite3.connect(self.app.config["DATABASE"])
        conn.execute("""INSERT INTO users (name, email, password_hash, batch_year, role, status)
                        VALUES ('Admin User', 'admin@test.local', ?, 2000, 'admin', 'approved')""",
                     (generate_password_hash(TEST_PW),))
        conn.commit()
        conn.close()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def admin(self):
        a = ApiClient(self.app)
        self.assertEqual(a.post("/api/auth/login", {"email": "admin@test.local", "password": TEST_PW}).status_code, 200)
        return a

    def signup(self, email="ravi@test.local", name="Ravi Kumar", batch=2015):
        c = ApiClient(self.app)
        r = c.post("/api/auth/signup", {"name": name, "email": email, "password": TEST_PW, "batch_year": batch,
                                        "last_class": "XII", "stream": "Science", "city": "Chennai", "agree": True})
        return c, r

    def test_me_and_csrf(self):
        c = ApiClient(self.app)
        me = c.get("/api/me").get_json()
        self.assertIsNone(me["user"])
        self.assertEqual(me["school"]["established"], 1986)
        r = c.c.post("/api/auth/login", json={"email": "admin@test.local", "password": TEST_PW})
        self.assertEqual(r.status_code, 400)
        self.assertIn("error", r.get_json())

    def test_parallel_first_visit_keeps_token_valid(self):
        # A browser's first visit fetches /api/me and /api/home in parallel, with no cookie yet.
        # Only /api/me may start a session; otherwise the browser can keep /api/home's cookie
        # while the page holds /api/me's token, and every form then fails the CSRF check.
        me_client, home_client = self.app.test_client(), self.app.test_client()
        token = me_client.get("/api/me").get_json()["csrf"]
        home = home_client.get("/api/home")
        self.assertNotIn("session=", home.headers.get("Set-Cookie", ""))
        r = me_client.post("/api/auth/login", json={"email": "admin@test.local", "password": TEST_PW},
                           headers={"X-CSRF-Token": token})
        self.assertEqual(r.status_code, 200)

    def test_auth_errors_are_json(self):
        c = ApiClient(self.app)
        self.assertEqual(c.get("/api/dashboard").status_code, 401)
        self.assertEqual(c.get("/api/nothing-here").get_json()["error"], "We couldn't find that page.")
        r = c.post("/api/auth/login", {"email": "admin@test.local", "password": "wrong-pass1"})
        self.assertEqual(r.status_code, 401)

    def test_signup_pending_then_approved_flow(self):
        alum, r = self.signup()
        self.assertEqual(r.status_code, 201)
        user = r.get_json()["user"]
        self.assertEqual(user["status"], "pending")
        self.assertNotIn("password_hash", user)
        self.assertEqual(alum.get("/api/directory").status_code, 403)
        _, dup = self.signup()
        self.assertIn("already exists", dup.get_json()["error"])

        admin = self.admin()
        self.assertEqual(alum.get("/api/admin").status_code, 403)
        pending = admin.get("/api/admin").get_json()["users"]
        self.assertEqual([u["email"] for u in pending], ["ravi@test.local"])
        admin.post(f"/api/admin/users/{user['id']}/approve")

        d = alum.get("/api/dashboard").get_json()
        self.assertIn("completeness", d)
        people = alum.get("/api/directory?q=ravi&batch=2015").get_json()["people"]
        self.assertEqual(len(people), 1)

        # events + rsvp
        self.assertEqual(alum.post("/api/events", {"title": "x"}).status_code, 403)
        eid = admin.post("/api/events", {"title": "Meet", "description": "Reunion", "location": "Hall",
                                         "starts_at": "2099-02-01T10:00"}).get_json()["id"]
        self.assertTrue(alum.post(f"/api/events/{eid}/rsvp").get_json()["mine"])
        self.assertEqual(len(alum.get(f"/api/events/{eid}").get_json()["attendees"]), 1)

        # jobs, memories, news
        jid = alum.post("/api/jobs", {"title": "Intern", "company": "Acme", "job_type": "Internship",
                                      "description": "Python"}).get_json()["id"]
        meena, _ = self.signup("meena@test.local", "Meena S", 2012)
        mid = [u for u in admin.get("/api/admin").get_json()["users"] if u["email"] == "meena@test.local"][0]["id"]
        admin.post(f"/api/admin/users/{mid}/approve")
        self.assertEqual(meena.post(f"/api/jobs/{jid}/delete").status_code, 403)
        alum.post("/api/memories", {"body": "Sports day on the big ground"})
        self.assertEqual(len(meena.get("/api/memories").get_json()["items"]), 1)
        admin.post("/api/news", {"title": "Hello", "body": "Welcome"})
        self.assertEqual(len(ApiClient(self.app).get("/api/news").get_json()["items"]), 1)

        # contact privacy
        person = meena.get(f"/api/alumni/{user['id']}").get_json()["person"]
        self.assertNotIn("email", person)

        # profile update + photo
        r = alum.send("put", "/api/profile", {"name": "Ravi Kumar", "batch_year": 2015, "last_class": "XII",
                                             "occupation": "Engineer", "show_contact": True})
        self.assertEqual(r.get_json()["user"]["occupation"], "Engineer")
        self.assertIn("email", meena.get(f"/api/alumni/{user['id']}").get_json()["person"])
        png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 40
        r = alum.post("/api/profile/photo", data={"photo": (io.BytesIO(png), "me.png")},
                      content_type="multipart/form-data")
        self.assertTrue(r.get_json()["photo_url"].startswith("/uploads/"))

        # suspension
        admin.post(f"/api/admin/users/{user['id']}/suspend")
        self.assertEqual(alum.get("/api/dashboard").status_code, 401)

    def test_logout(self):
        a = self.admin()
        self.assertIsNotNone(a.get("/api/me").get_json()["user"])
        a.post("/api/auth/logout")
        self.assertIsNone(a.get("/api/me").get_json()["user"])


if __name__ == "__main__":
    unittest.main()
