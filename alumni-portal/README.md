# Alumni Portal: PM SHRI Kendriya Vidyalaya No. 2 Pondicherry

A website where former students of KV No. 2 Pondicherry (Kalapet, est. 1986) can register, get verified by the school,
find their batchmates, RSVP for reunions, share jobs, offer to mentor students, and post memories.

It has two parts:

| Part | Tech | Port |
|---|---|---|
| **Website** (`web/`) | Next.js 16 + React 19, white/blue/yellow school theme, subtle Three.js hero (`@react-three/fiber`) | 3000 |
| **Server** (this folder) | Python + Flask JSON API (`api.py`), SQLite database (`instance/portal.db`) | 5000 |

The website forwards `/api/*` and `/uploads/*` to Flask, so the login cookie works on one address.
Flask also still serves a simpler HTML version of the portal at port 5000 as a fallback.

## Quick start (Windows)

The first time only, create the school coordinator account:

```bat
cd alumni-portal
python manage.py create-admin
```

Then start both servers:

```bat
start.bat
```

Then open **http://localhost:3000**.

Or by hand, in two terminals:

```bash
pip install -r requirements.txt
python manage.py create-admin      # first time only
python manage.py seed-demo         # optional: sample event, announcement and job
python app.py                      # API on http://127.0.0.1:5000
```

```bash
cd web
npm install                        # first time only
npm run dev                        # website on http://localhost:3000
```

The database and tables are created automatically the first time the server runs.
For production: `npm run build` then `npm start` in `web/`, with `API_URL` set if Flask runs somewhere other than `http://127.0.0.1:5000`.

## Design

See [web/DESIGN_SYSTEM.md](web/DESIGN_SYSTEM.md) for the colour, type, glass and spacing tokens, the component variants and the copy rules.
The KVS and PM SHRI logos in `web/public/brand/` come from the header of the school's official website. Get the school's approval before the portal goes public.

## Features

| Area | What it does |
|---|---|
| **Sign up / sign in** | Registration collects batch year, last class, stream, house, admission no., current work and city. Passwords are salted and hashed with Werkzeug (scrypt) before storage. Plain passwords are never saved. Users can also change their password. |
| **Verification** | New accounts start as *pending*. A coordinator approves or rejects them in the Admin panel. Until then, pending users can only edit their own profile. Set `REQUIRE_APPROVAL=0` to approve everyone automatically. |
| **Dashboard** | Profile-completeness meter, upcoming events with one-click RSVP, batchmates, latest jobs and news. |
| **Directory** | Search by name, profession or company, and filter by batch, city or "mentors only". |
| **Profiles** | Photo upload, bio, LinkedIn. Email and phone appear only if the person opts in. |
| **Events** | Admins create events. Alumni RSVP and can see who else is attending. |
| **Jobs** | Any verified alum can post a job or internship, then close, reopen or delete their own listings. |
| **Memories wall** | A shared board for school memories. |
| **News** | Public announcements. Only admins can post them. |
| **Admin** | Approve, reject, suspend or restore accounts, promote or demote admins, delete users. Also shows stats and an alumni-by-batch chart. |

## Security

- Passwords are hashed (scrypt). After 5 wrong passwords in a row, that email and IP pair is locked out for 10 minutes.
- Every form has a CSRF token. Session cookies are HttpOnly and SameSite=Lax.
- Each session checks that the user is still approved, so suspended users are signed out immediately.
- Uploads must be PNG, JPG or WEBP, and the file contents are checked too. Files are renamed to random names, capped at 3 MB, and only signed-in users can view them.
- Login redirects can only point to pages on this site, which blocks open redirects. All database queries are parameterised.
- The session secret key is generated once and saved in `instance/secret_key`. You can override it with the `SECRET_KEY` env var.

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | auto-generated | Session signing key |
| `PORTAL_DB` | `instance/portal.db` | Database file path |
| `REQUIRE_APPROVAL` | `1` | `0` = approve signups automatically |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Where the server listens (`HOST=0.0.0.0` makes it reachable on the school LAN) |
| `SESSION_COOKIE_SECURE` | off | Set to `1` when serving over HTTPS |

## Tests

```bash
python -m unittest discover tests
```

There are 15 tests. `test_api.py` covers the JSON API used by the website. The 11 tests in `test_portal.py` cover signup, hashed storage, validation, CSRF, login and lockout, the approval flow, directory search, events and RSVP, job permissions, the memories wall, contact privacy, photo upload checks, password change and suspension.

## Deploying for the school

For real use, run it behind a production server over HTTPS. For example:

```bash
pip install waitress
waitress-serve --port=8000 app:app
```

Put Nginx or IIS in front with an SSL certificate, and set `SESSION_COOKIE_SECURE=1` and a fixed `SECRET_KEY`.
Back up `instance/portal.db` and `instance/uploads/` regularly.

## Project layout

```
alumni-portal/
  web/             Next.js frontend: app/ (pages), components/ (Nav, Crest, HeroScene, ui), lib/ (api client)
  api.py           JSON API for the website
  core.py          shared validation and helpers
  app.py           Flask app, HTML fallback pages, CSRF, error handling
  db.py            SQLite helpers
  schema.sql       tables: users, events, rsvps, jobs, announcements, memories
  manage.py        create-admin, seed-demo
  templates/       Jinja pages (+ _macros.html for shared form fields and avatars)
  static/style.css
  tests/
  instance/        created at runtime: database, uploads, secret key (git-ignored)
```
