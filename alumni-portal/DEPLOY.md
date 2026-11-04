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

## Updating the API later

After you merge new changes, open a PythonAnywhere **Bash** console and run:

```bash
cd ~/Alumni-portal && git pull
```

Then click **Reload** on the Web tab. Your database and photos are not touched, because `instance/` is git-ignored.

## Free-plan limits to know

- **PythonAnywhere:** you must log in once every **3 months** and click **"Run until 3 months from today"** on the Web tab, or the API is switched off. You get 512 MB of disk and a daily CPU allowance, which is plenty for a school alumni portal.
- **Vercel Hobby:** for non-commercial use, which an alumni association is.
- **Backups:** download `instance/portal.db` from PythonAnywhere's **Files** tab now and then, to keep a copy.

## Troubleshooting

| Problem | Fix |
|---|---|
| Website says "Can't reach the server" | Check that `API_URL` in Vercel matches your PythonAnywhere address exactly, then redeploy on Vercel. |
| PythonAnywhere shows "Something went wrong" | Open the **error log** link on the Web tab. Usually the username in the WSGI file is wrong. |
| Signed in, but sent straight back to the login page | Make sure **Force HTTPS** is on at PythonAnywhere, and that you're opening the `https://` Vercel address. |
