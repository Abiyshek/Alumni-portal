"""
WSGI entry point for PythonAnywhere.

Paste this whole file into the WSGI configuration file linked on your PythonAnywhere "Web" tab,
then replace YOUR_USERNAME below with your PythonAnywhere username. See DEPLOY.md.
"""

import os
import sys

PROJECT_DIR = "/home/YOUR_USERNAME/Alumni-portal/alumni-portal"

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)

# The site is served over HTTPS (via Vercel and pythonanywhere.com), so only send the login cookie over HTTPS.
os.environ.setdefault("SESSION_COOKIE_SECURE", "1")

from app import app as application  # noqa: E402
