# Deploying the alumni portal for free

| Part | Free host | Address you get |
|---|---|---|
| Flask API + SQLite database + photos | **PythonAnywhere** (Beginner plan) | `https://YOUR_USERNAME.pythonanywhere.com` |
| Next.js website | **Vercel** (Hobby plan) | `https://your-project.vercel.app` |

The website forwards `/api/*` and `/uploads/*` to PythonAnywhere, so visitors only ever see the Vercel address and logins work normally.
PythonAnywhere keeps your files permanently, so the database (`instance/portal.db`) and uploaded photos survive restarts.

Merge the pull request into `main` first, because both hosts deploy from `main`.

---

## Part 1: API on PythonAnywhere (about 10 minutes)

1. Sign up for a free **Beginner** account at https://www.pythonanywhere.com/. Your username becomes part of the API address.
2. Open **Consoles → Bash** and run:

   ```bash
   git clone https://github.com/Abiyshek/Alumni-portal.git
   cd Alumni-portal/alumni-portal
   pip3.12 install --user -r requirements.txt
   python3.12 manage.py create-admin
   ```

   `create-admin` asks for your email, name and a password. This is the school coordinator account.
   You can also run `python3.12 manage.py seed-demo` to add a sample event, announcement and job.

3. Go to the **Web** tab → **Add a new web app** → **Next** → **Manual configuration** → **Python 3.12** → **Next**.
4. On the same Web tab, under **Code**, click the **WSGI configuration file** link. Delete everything in it, paste in the contents of
   [`deploy/pythonanywhere_wsgi.py`](deploy/pythonanywhere_wsgi.py), change `YOUR_USERNAME` to your username, and click **Save**.
5. Back on the Web tab, turn on **Force HTTPS**, then click the green **Reload** button.
6. Check that it works: open `https://YOUR_USERNAME.pythonanywhere.com/api/me` in your browser. You should see some JSON that includes `"school"`.

## Part 2: Website on Vercel (about 5 minutes)

1. Sign up at https://vercel.com/ with **Continue with GitHub**.
2. Click **Add New… → Project** and import **Abiyshek/Alumni-portal**.
3. Set these, then click **Deploy**:
   - **Root Directory:** `alumni-portal/web`
   - **Framework Preset:** Next.js (detected automatically)
   - **Environment Variables:** add `API_URL` = `https://YOUR_USERNAME.pythonanywhere.com` (no slash at the end)
4. When it finishes, open the `.vercel.app` address and sign in with the coordinator account from Part 1.

From now on, every push to `main` redeploys the website automatically.

---

## Faster option: deploy from your own computer

Parts 1 and 2 can also be done from the command line, with no dashboard clicks.

1. Save your PythonAnywhere API token (Account → API Token) in the file `~/.pythonanywhere_token`.
2. Run `python manage.py create-admin` locally, then:

   ```bash
   python deploy/pythonanywhere_deploy.py YOUR_USERNAME --with-db
   ```

   This uploads the code and your local database, creates and configures the web app, reloads it, and checks `/api/me`.
   Leave out `--with-db` on later updates, because it would overwrite the live database.
3. For the website, create the Vercel project from GitHub as in Part 2, with **Root Directory** set to `alumni-portal/web`.
   Don't run `vercel deploy` from inside `web/`: once the root directory is set, Vercel looks for `alumni-portal/web` inside that folder and the deploy fails.

The live portal is at https://kv2-alumni-portal.vercel.app, with its API at https://sheky.pythonanywhere.com.

## Updating the site later

- **Website:** merge into `main`. Vercel builds and deploys it automatically, and every pull request also gets a preview build.
- **API:** from `alumni-portal/` on your computer, run:

  ```bash
  python deploy/pythonanywhere_deploy.py sheky
  ```

  This uploads the new code and reloads the app. Without `--with-db`, your database and photos aren't touched.
  If you set up the API with `git clone` (Part 1) instead, run `cd ~/Alumni-portal && git pull` in a PythonAnywhere Bash console and click **Reload**.

## Notifications

When news, a job or an event is posted, members are notified four ways:

| Channel | Setup needed |
|---|---|
| 🔔 Bell in the header | None. It always works. |
| 💬 WhatsApp "Share" button | None. Coordinators tap it and forward the post to the alumni group. |
| 📲 Phone and browser alerts | None. Members switch them on from the bell. On iPhone, they first add the site to the Home Screen (Share → Add to Home Screen). Keys are created on the server automatically. |
| 📧 Email | One-time setup below. Until then, members' email choices are saved, but nothing is sent. |

### Email notifications (one-time setup)

1. Use a Gmail account for the alumni association, and turn on **2-Step Verification** for it.
2. Create an **App Password** at https://myaccount.google.com/apppasswords. Google shows a 16-letter password.
3. On your computer, create the file `~/.alumni_smtp.json`:

   ```json
   {"host": "smtp.gmail.com", "port": 587, "user": "your.alumni.account@gmail.com",
    "password": "the 16-letter app password", "from": "KV2 Alumni <your.alumni.account@gmail.com>"}
   ```

4. From `alumni-portal/`, run `python deploy/pythonanywhere_deploy.py sheky --with-smtp`.

Every email has a one-click **Stop these emails** link, and members can switch emails on or off from the bell.

## Free-plan limits to know

- **PythonAnywhere:** you must log in once every **3 months** and click **"Run until 3 months from today"** on the Web tab, or the API is switched off. You get 512 MB of disk and a daily CPU allowance, which is plenty for a school alumni portal.
- **Vercel Hobby:** for non-commercial use, which an alumni association is.
- **Gmail:** sends up to about 500 emails a day, which is plenty for an alumni group of a few hundred.
- **PythonAnywhere free:** outgoing connections are limited to an approved list of sites. Gmail's mail server and the major push services (Google/Chrome, Mozilla/Firefox, Apple) normally work. If a push or email fails, the reason is in the web app's **error log**.
- **Backups:** download `instance/portal.db` from PythonAnywhere's **Files** tab now and then, to keep a copy.

## Troubleshooting

| Problem | Fix |
|---|---|
| Website says "Can't reach the server" | Check that `API_URL` in Vercel matches your PythonAnywhere address exactly, then redeploy on Vercel. |
| PythonAnywhere shows "Something went wrong" | Open the **error log** link on the Web tab. Usually the username in the WSGI file is wrong. |
| Signed in, but sent straight back to the login page | Make sure **Force HTTPS** is on at PythonAnywhere, and that you're opening the `https://` Vercel address. |
