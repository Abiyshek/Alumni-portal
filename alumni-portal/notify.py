"""
Notifications when news, a job or an event is posted.

- Bell: computed from the content tables in api.py (no sending needed).
- Email: SMTP settings in instance/smtp.json (see DEPLOY.md). Skipped when that file is missing.
- Push: standard Web Push (RFC 8291 aes128gcm + VAPID, RFC 8292) using the `cryptography` package.
  VAPID keys are generated once into instance/vapid.json. Skipped if `cryptography` is unavailable.

Sending runs in a background thread so posting stays fast; set NOTIFY_SYNC for tests.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import smtplib
import ssl
import struct
import threading
import time
import urllib.error
import urllib.request
from email.message import EmailMessage
from urllib.parse import urlparse

from flask import current_app, request
from itsdangerous import BadSignature, URLSafeSerializer

from db import execute, query

log = logging.getLogger(__name__)

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAVE_CRYPTO = True
except ImportError:  # push is optional
    HAVE_CRYPTO = False

KIND_LABEL = {"news": "📢 News", "job": "💼 New opportunity", "event": "📅 New event"}


# ---------------------------------------------------------------- helpers

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def instance_path(name):
    return os.path.join(os.path.dirname(current_app.config["DATABASE"]), name)


def site_url():
    """Public address of the website (the Vercel proxy forwards the visitor's host)."""
    if current_app.config.get("SITE_URL"):
        return current_app.config["SITE_URL"].rstrip("/")
    host = request.headers.get("X-Forwarded-Host") or request.host
    return f"https://{host.split(',')[0].strip()}"


def unsubscribe_token(user_id):
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="email-unsubscribe").dumps(user_id)


def user_from_unsubscribe_token(token):
    try:
        return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="email-unsubscribe").loads(token)
    except BadSignature:
        return None


# ---------------------------------------------------------------- email

def smtp_settings():
    path = instance_path("smtp.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg if cfg.get("host") and cfg.get("user") and cfg.get("password") else None


def send_emails(cfg, messages):
    port = int(cfg.get("port", 587))
    context = ssl.create_default_context()
    if port == 465:
        server = smtplib.SMTP_SSL(cfg["host"], port, context=context, timeout=30)
    else:
        server = smtplib.SMTP(cfg["host"], port, timeout=30)
        server.starttls(context=context)
    with server:
        server.login(cfg["user"], cfg["password"])
        for msg in messages:
            try:
                server.send_message(msg)
            except smtplib.SMTPException as exc:
                log.warning("email to %s failed: %s", msg["To"], exc)


def build_email(cfg, to, title, kind, summary, link, unsubscribe_link):
    msg = EmailMessage()
    msg["Subject"] = f"{KIND_LABEL[kind]}: {title}"
    msg["From"] = cfg.get("from") or cfg["user"]
    msg["To"] = to
    msg["List-Unsubscribe"] = f"<{unsubscribe_link}>"
    text = f"{summary}\n\nOpen it: {link}\n\n--\nKV No. 2 Pondicherry Alumni Association\nStop these emails: {unsubscribe_link}\n"
    msg.set_content(text)
    esc = lambda s: (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    msg.add_alternative(f"""<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;color:#142037">
  <div style="background:#0d3384;color:#fff;padding:16px 20px;border-bottom:4px solid #f5b301">
    <b>PM SHRI KV No. 2 Pondicherry</b><br><span style="font-size:13px">Alumni Association</span></div>
  <div style="padding:20px;border:1px solid #e3e8f1;border-top:0">
    <p style="color:#1446a0;font-size:13px;margin:0 0 6px">{esc(KIND_LABEL[kind])}</p>
    <h2 style="margin:0 0 12px;color:#0a2463">{esc(title)}</h2>
    <p style="white-space:pre-wrap;color:#4a5671">{esc(summary)}</p>
    <p><a href="{link}" style="display:inline-block;background:#1446a0;color:#fff;padding:10px 18px;border-radius:8px;text-decoration:none">Open on the portal</a></p>
  </div>
  <p style="font-size:12px;color:#7a859e;text-align:center">You get this because you're a member of the alumni portal.
    <a href="{unsubscribe_link}" style="color:#7a859e">Stop these emails</a></p></div>""", subtype="html")
    return msg


# ---------------------------------------------------------------- web push

def vapid_keys():
    """(private_key, public_key_b64url), created on first use. None if push isn't available."""
    if not HAVE_CRYPTO:
        return None
    path = instance_path("vapid.json")
    if not os.path.exists(path):
        key = ec.generate_private_key(ec.SECP256R1())
        pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                serialization.NoEncryption()).decode()
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"private_pem": pem}, f)
    with open(path, encoding="utf-8") as f:
        key = serialization.load_pem_private_key(json.load(f)["private_pem"].encode(), password=None)
    public = key.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    return key, b64url(public)


def _hkdf(salt, ikm, info, length):
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    return hmac.new(prk, info + b"\x01", hashlib.sha256).digest()[:length]


def encrypt_push(payload, p256dh, auth, salt=None, server_key=None):
    """RFC 8291 aes128gcm encryption of `payload` for one subscription. Returns the request body."""
    ua_public = b64url_decode(p256dh)
    auth_secret = b64url_decode(auth)
    server_key = server_key or ec.generate_private_key(ec.SECP256R1())
    as_public = server_key.public_key().public_bytes(serialization.Encoding.X962,
                                                     serialization.PublicFormat.UncompressedPoint)
    ua_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), ua_public)
    shared = server_key.exchange(ec.ECDH(), ua_key)
    ikm = _hkdf(auth_secret, shared, b"WebPush: info\x00" + ua_public + as_public, 32)
    salt = salt or os.urandom(16)
    cek = _hkdf(salt, ikm, b"Content-Encoding: aes128gcm\x00", 16)
    nonce = _hkdf(salt, ikm, b"Content-Encoding: nonce\x00", 12)
    ciphertext = AESGCM(cek).encrypt(nonce, payload + b"\x02", None)
    return salt + struct.pack("!IB", 4096, len(as_public)) + as_public + ciphertext


def vapid_header(endpoint, key, public_b64, subject):
    url = urlparse(endpoint)
    header = b64url(json.dumps({"typ": "JWT", "alg": "ES256"}).encode())
    claims = b64url(json.dumps({"aud": f"{url.scheme}://{url.netloc}", "exp": int(time.time()) + 12 * 3600,
                                "sub": subject}).encode())
    r, s = decode_dss_signature(key.sign(f"{header}.{claims}".encode(), ec.ECDSA(hashes.SHA256())))
    token = f"{header}.{claims}.{b64url(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}"
    return f"vapid t={token}, k={public_b64}"


def send_push(sub, payload, key, public_b64, subject):
    """Returns False when the subscription is gone and should be deleted."""
    body = encrypt_push(json.dumps(payload).encode(), sub["p256dh"], sub["auth"])
    req = urllib.request.Request(sub["endpoint"], data=body, method="POST", headers={
        "Content-Encoding": "aes128gcm", "Content-Type": "application/octet-stream", "TTL": "86400",
        "Urgency": "normal", "Authorization": vapid_header(sub["endpoint"], key, public_b64, subject)})
    try:
        with urllib.request.urlopen(req, timeout=20):
            return True
    except urllib.error.HTTPError as exc:
        if exc.code in (404, 410):
            return False
        log.warning("push to %s failed: HTTP %s", urlparse(sub["endpoint"]).netloc, exc.code)
    except (urllib.error.URLError, OSError) as exc:
        log.warning("push to %s failed: %s", urlparse(sub["endpoint"]).netloc, exc)
    return True


# ---------------------------------------------------------------- fan-out

def notify_new_post(kind, title, summary, path, actor_id):
    """Email and push every approved member (except the poster) about a new news item, job or event."""
    app = current_app._get_current_object()
    site = site_url()
    link = site + path
    cfg = smtp_settings()
    emails = []
    if cfg:
        for u in query("""SELECT id, email FROM users WHERE status='approved' AND notify_email=1 AND id<>?""",
                       (actor_id,)):
            unsub = f"{site}/unsubscribe?token={unsubscribe_token(u['id'])}"
            emails.append(build_email(cfg, u["email"], title, kind, summary[:600], link, unsub))
    keys = vapid_keys()
    subs = [dict(r) for r in query("""SELECT s.* FROM push_subscriptions s JOIN users u ON u.id=s.user_id
                                      WHERE u.status='approved' AND s.user_id<>?""", (actor_id,))] if keys else []
    payload = {"title": f"{KIND_LABEL[kind]}: {title}", "body": summary[:140], "url": link}

    def work():
        if emails:
            try:
                send_emails(cfg, emails)
            except (smtplib.SMTPException, OSError) as exc:
                log.warning("email notifications failed: %s", exc)
        dead = [s["endpoint"] for s in subs if not send_push(s, payload, keys[0], keys[1], site)]
        if dead:
            with app.app_context():
                for endpoint in dead:
                    execute("DELETE FROM push_subscriptions WHERE endpoint=?", (endpoint,))

    if app.config.get("NOTIFY_SYNC"):
        work()
    else:
        threading.Thread(target=work, daemon=True).start()
    return {"emails": len(emails), "push": len(subs)}
