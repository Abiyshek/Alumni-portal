"""
Deploy (or update) the Flask API on PythonAnywhere using its HTTP API, with no browser clicks.

    python deploy/pythonanywhere_deploy.py YOUR_USERNAME [--with-db] [--eu]

The API token is read from the file ~/.pythonanywhere_token (PythonAnywhere: Account -> API Token).
--with-db  also uploads instance/portal.db (first deploy only: it would overwrite live data later)
--eu       for accounts on eu.pythonanywhere.com
--with-smtp also uploads email settings from ~/.alumni_smtp.json (see DEPLOY.md, "Email notifications")
"""

import argparse
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
CODE_FILES = ["app.py", "api.py", "core.py", "db.py", "notify.py", "manage.py", "schema.sql", "requirements.txt"]
CODE_DIRS = ["templates", "static"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username")
    ap.add_argument("--with-db", action="store_true")
    ap.add_argument("--eu", action="store_true")
    ap.add_argument("--with-smtp", action="store_true")
    args = ap.parse_args()

    token_path = os.path.expanduser("~/.pythonanywhere_token")
    if not os.path.exists(token_path):
        sys.exit(f"Save your PythonAnywhere API token in {token_path} first.")
    with open(token_path) as f:
        token = f.read().strip()

    user = args.username
    host = "eu.pythonanywhere.com" if args.eu else "www.pythonanywhere.com"
    domain = f"{user}.{'eu.' if args.eu else ''}pythonanywhere.com"
    base = f"https://{host}/api/v0/user/{user}"
    remote_root = f"/home/{user}/Alumni-portal/alumni-portal"
    s = requests.Session()
    s.headers["Authorization"] = f"Token {token}"

    def check(r, what):
        if r.status_code >= 400:
            sys.exit(f"{what} failed: HTTP {r.status_code} {r.text[:300]}")
        return r

    def upload(local, remote):
        with open(local, "rb") as fh:
            check(s.post(f"{base}/files/path{remote}", files={"content": fh}), f"Upload {remote}")

    check(s.get(f"{base}/cpu/"), "Token check (is the username right?)")
    print(f"Authenticated as {user}.")

    files = [f for f in CODE_FILES]
    for d in CODE_DIRS:
        for root, _, names in os.walk(os.path.join(PROJECT, d)):
            files += [os.path.relpath(os.path.join(root, n), PROJECT).replace("\\", "/") for n in names]
    if args.with_db:
        files.append("instance/portal.db")
    for rel in files:
        upload(os.path.join(PROJECT, rel), f"{remote_root}/{rel}")
    print(f"Uploaded {len(files)} files to {remote_root}.")
    if args.with_smtp:
        smtp_path = os.path.expanduser("~/.alumni_smtp.json")
        if not os.path.exists(smtp_path):
            sys.exit(f"--with-smtp: create {smtp_path} first (see DEPLOY.md).")
        upload(smtp_path, f"{remote_root}/instance/smtp.json")
        print("Uploaded email settings.")

    apps = check(s.get(f"{base}/webapps/"), "List web apps").json()
    if not any(a["domain_name"] == domain for a in apps):
        check(s.post(f"{base}/webapps/", data={"domain_name": domain, "python_version": "python312"}), "Create web app")
        print(f"Created web app {domain}.")

    with open(os.path.join(HERE, "pythonanywhere_wsgi.py"), encoding="utf-8") as fh:
        wsgi = fh.read().replace("YOUR_USERNAME", user)
    wsgi_path = f"/var/www/{domain.replace('.', '_')}_wsgi.py"
    check(s.post(f"{base}/files/path{wsgi_path}", files={"content": ("wsgi.py", wsgi.encode())}), "Upload WSGI file")

    check(s.patch(f"{base}/webapps/{domain}/", data={"force_https": "true", "source_directory": remote_root}), "Configure web app")
    check(s.post(f"{base}/webapps/{domain}/reload/"), "Reload web app")
    print("Reloaded. Checking the API...")

    for _ in range(10):
        time.sleep(3)
        r = requests.get(f"https://{domain}/api/me", timeout=30)
        if r.ok and "school" in r.text:
            print(f"Live: https://{domain}/api/me")
            return
    log = s.get(f"{base}/files/path/var/log/{domain}.error.log")
    tail = log.text[-1500:] if log.ok else "(no error log)"
    sys.exit(f"API did not respond correctly (HTTP {r.status_code}). Error log tail:\n{tail}")


if __name__ == "__main__":
    main()
