"""Tests for notifications: the bell feed, email, unsubscribe links and Web Push."""

import base64
import hashlib
import hmac
import json
import os
import shutil
import sqlite3
import struct
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.hazmat.primitives import hashes, serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import ec  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature  # noqa: E402
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

import app as portal  # noqa: E402
import notify  # noqa: E402
from test_api import TEST_PW, ApiClient  # noqa: E402


def b64d(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def hkdf(salt, ikm, info, length):
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    return hmac.new(prk, info + b"\x01", hashlib.sha256).digest()[:length]


def decrypt_like_a_browser(body, receiver_key, auth):
    """RFC 8291 decryption, written independently of notify.py, as a phone's push service client would do it."""
    salt, (rs, idlen) = body[:16], struct.unpack("!IB", body[16:21])
    as_public = body[21:21 + idlen]
    ciphertext = body[21 + idlen:]
    ua_public = receiver_key.public_key().public_bytes(serialization.Encoding.X962,
                                                       serialization.PublicFormat.UncompressedPoint)
    shared = receiver_key.exchange(ec.ECDH(), ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), as_public))
    ikm = hkdf(auth, shared, b"WebPush: info\x00" + ua_public + as_public, 32)
    cek = hkdf(salt, ikm, b"Content-Encoding: aes128gcm\x00", 16)
    nonce = hkdf(salt, ikm, b"Content-Encoding: nonce\x00", 12)
    plain = AESGCM(cek).decrypt(nonce, ciphertext, None)
    assert rs == 4096 and plain.endswith(b"\x02")
    return plain[:-1]


def new_subscription():
    key = ec.generate_private_key(ec.SECP256R1())
    auth = os.urandom(16)
    pub = key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    enc = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
    return key, auth, {"endpoint": "https://fcm.googleapis.com/fcm/send/test-device",
                       "keys": {"p256dh": enc(pub), "auth": enc(auth)}}


class NotificationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        portal._failed_logins.clear()
        self.db = os.path.join(self.tmp, "t.db")
        self.app = portal.create_app({"TESTING": True, "DATABASE": self.db, "UPLOAD_FOLDER": os.path.join(self.tmp, "up"),
                                      "REQUIRE_APPROVAL": True, "NOTIFY_SYNC": True,
                                      "SITE_URL": "https://alumni.example"})
        conn = sqlite3.connect(self.db)
        h = generate_password_hash(TEST_PW)
        conn.execute("INSERT INTO users (name,email,password_hash,batch_year,role,status) "
                     "VALUES ('Admin User','admin@test.local',?,2000,'admin','approved')", (h,))
        conn.execute("INSERT INTO users (name,email,password_hash,batch_year,status) "
                     "VALUES ('Ravi Kumar','ravi@test.local',?,2015,'approved')", (h,))
        conn.execute("INSERT INTO users (name,email,password_hash,batch_year,status,notify_email) "
                     "VALUES ('Quiet Person','quiet@test.local',?,2016,'approved',0)", (h,))
        conn.execute("INSERT INTO users (name,email,password_hash,batch_year,status) "
                     "VALUES ('Not Yet','pending@test.local',?,2017,'pending')", (h,))
        # pretend everyone joined a while ago, so new posts count as unread
        conn.execute("UPDATE users SET created_at = datetime('now', '-1 day')")
        conn.commit()
        conn.close()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def login(self, email):
        c = ApiClient(self.app)
        self.assertEqual(c.post("/api/auth/login", {"email": email, "password": TEST_PW}).status_code, 200)
        return c

    def post_all(self, admin):
        admin.post("/api/news", {"title": "Reunion date fixed", "body": "Save the date!"})
        admin.post("/api/jobs", {"title": "Intern", "company": "Acme", "job_type": "Internship", "description": "Python"})
        admin.post("/api/events", {"title": "Alumni Meet", "description": "Lunch", "location": "Hall",
                                   "starts_at": "2099-01-10T10:00"})

    # ---- bell

    def test_bell_shows_new_posts_until_seen(self):
        admin, ravi = self.login("admin@test.local"), self.login("ravi@test.local")
        self.assertEqual(ravi.get("/api/notifications").get_json()["unread"], 0)
        self.post_all(admin)
        feed = ravi.get("/api/notifications").get_json()
        self.assertEqual(feed["unread"], 3)
        self.assertEqual({i["kind"] for i in feed["items"]}, {"news", "job", "event"})
        self.assertIn("/events/1", [i["path"] for i in feed["items"]])
        # your own posts never notify you
        self.assertEqual(admin.get("/api/notifications").get_json()["unread"], 0)
        ravi.post("/api/notifications/seen")
        self.assertEqual(ravi.get("/api/notifications").get_json()["unread"], 0)
        # pending members can't use the bell
        self.assertEqual(self.login("pending@test.local").get("/api/notifications").status_code, 403)

    # ---- email

    def write_smtp(self):
        with open(os.path.join(self.tmp, "smtp.json"), "w") as f:
            json.dump({"host": "smtp.gmail.com", "port": 587, "user": "portal@example.com", "password": "app-password",
                       "from": "KV2 Alumni <portal@example.com>"}, f)

    def test_email_goes_to_opted_in_members_only(self):
        admin = self.login("admin@test.local")
        admin.post("/api/news", {"title": "No email yet", "body": "smtp.json missing"})  # no settings: nothing sent
        self.write_smtp()
        with mock.patch("notify.smtplib.SMTP") as smtp:
            admin.post("/api/news", {"title": "Reunion date fixed", "body": "Save the date!"})
        server = smtp.return_value
        server.login.assert_called_once_with("portal@example.com", "app-password")
        sent = [call.args[0] for call in server.send_message.call_args_list]
        self.assertEqual([m["To"] for m in sent], ["ravi@test.local"])  # not the poster, opted-out or pending
        self.assertIn("Reunion date fixed", sent[0]["Subject"])
        body = sent[0].get_body(("plain",)).get_content()
        self.assertIn("https://alumni.example/news", body)
        self.assertIn("https://alumni.example/unsubscribe?token=", body)

    def test_unsubscribe_link_and_settings(self):
        ravi = self.login("ravi@test.local")
        with self.app.test_request_context():
            token = notify.unsubscribe_token(2)
        stranger = ApiClient(self.app)
        self.assertEqual(stranger.post("/api/notifications/unsubscribe", {"token": "forged"}).status_code, 404)
        self.assertEqual(stranger.post("/api/notifications/unsubscribe", {"token": token}).status_code, 200)
        self.assertFalse(ravi.get("/api/notifications").get_json()["notify_email"])
        ravi.send("put", "/api/notifications/settings", {"notify_email": True})
        self.assertTrue(ravi.get("/api/notifications").get_json()["notify_email"])

    # ---- web push

    def test_push_payload_decrypts_with_browser_keys(self):
        key, auth, sub = new_subscription()
        body = notify.encrypt_push(b'{"title":"Hello"}', sub["keys"]["p256dh"], sub["keys"]["auth"])
        self.assertEqual(decrypt_like_a_browser(body, key, auth), b'{"title":"Hello"}')

    def test_vapid_signature_verifies(self):
        with self.app.test_request_context():
            server_key, public = notify.vapid_keys()
            again = notify.vapid_keys()[1]
            header = notify.vapid_header("https://fcm.googleapis.com/fcm/send/x", server_key, public, "https://alumni.example")
        self.assertEqual(public, again)  # keys are created once and reused
        token = header.split("t=")[1].split(",")[0]
        h, c, s = token.split(".")
        claims = json.loads(b64d(c))
        self.assertEqual(claims["aud"], "https://fcm.googleapis.com")
        sig = b64d(s)
        der = encode_dss_signature(int.from_bytes(sig[:32], "big"), int.from_bytes(sig[32:], "big"))
        pub = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), b64d(public))
        pub.verify(der, f"{h}.{c}".encode(), ec.ECDSA(hashes.SHA256()))  # raises if invalid

    def test_push_sent_to_subscribers_and_dead_ones_removed(self):
        admin, ravi = self.login("admin@test.local"), self.login("ravi@test.local")
        key, auth, sub = new_subscription()
        self.assertEqual(ravi.post("/api/notifications/push", {"subscription": sub}).status_code, 201)
        self.assertEqual(ravi.post("/api/notifications/push", {"subscription": {"endpoint": "http://x"}}).status_code, 400)

        with mock.patch("notify.urllib.request.urlopen") as urlopen:
            admin.post("/api/events", {"title": "Alumni Meet", "description": "Lunch", "location": "Hall",
                                       "starts_at": "2099-01-10T10:00"})
        req = urlopen.call_args.args[0]
        self.assertEqual(req.full_url, sub["endpoint"])
        self.assertEqual(req.get_header("Content-encoding"), "aes128gcm")
        self.assertTrue(req.get_header("Authorization").startswith("vapid t="))
        payload = json.loads(decrypt_like_a_browser(req.data, key, auth))
        self.assertIn("Alumni Meet", payload["title"])
        self.assertEqual(payload["url"], "https://alumni.example/events/1")

        gone = urllib.error.HTTPError(sub["endpoint"], 410, "Gone", {}, None)
        with mock.patch("notify.urllib.request.urlopen", side_effect=gone):
            admin.post("/api/news", {"title": "Hello", "body": "World"})
        count = sqlite3.connect(self.db).execute("SELECT COUNT(*) FROM push_subscriptions").fetchone()[0]
        self.assertEqual(count, 0)  # expired subscriptions are cleaned up

    def test_existing_users_get_email_on_by_default(self):
        # build a database like the live one before this change: today's schema minus the two new columns
        old_db = os.path.join(self.tmp, "old.db")
        portal.create_app({"TESTING": True, "DATABASE": old_db, "UPLOAD_FOLDER": os.path.join(self.tmp, "up2")})
        conn = sqlite3.connect(old_db)
        conn.execute("ALTER TABLE users DROP COLUMN notify_email")
        conn.execute("ALTER TABLE users DROP COLUMN notif_seen_at")
        conn.execute("INSERT INTO users (name, email, password_hash, batch_year) VALUES ('Old', 'old@x', 'h', 2000)")
        conn.commit()
        conn.close()
        portal.create_app({"TESTING": True, "DATABASE": old_db, "UPLOAD_FOLDER": os.path.join(self.tmp, "up2")})
        row = sqlite3.connect(old_db).execute("SELECT notify_email, notif_seen_at FROM users").fetchone()
        self.assertEqual(row, (1, None))


if __name__ == "__main__":
    unittest.main()
