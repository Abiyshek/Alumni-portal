-- Alumni portal schema (SQLite)

CREATE TABLE IF NOT EXISTS users (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL,
    email            TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash    TEXT    NOT NULL,
    phone            TEXT,
    batch_year       INTEGER NOT NULL,            -- year they passed out / left
    last_class       TEXT    NOT NULL DEFAULT 'XII',
    stream           TEXT,                        -- Science / Commerce / Humanities ...
    house            TEXT,
    admission_no     TEXT,
    city             TEXT,
    country          TEXT    DEFAULT 'India',
    occupation       TEXT,
    organization     TEXT,
    industry         TEXT,
    linkedin         TEXT,
    bio              TEXT,
    photo            TEXT,
    willing_to_mentor INTEGER NOT NULL DEFAULT 0,
    show_contact     INTEGER NOT NULL DEFAULT 0,
    role             TEXT    NOT NULL DEFAULT 'alumni' CHECK (role IN ('alumni', 'admin')),
    status           TEXT    NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending', 'approved', 'rejected', 'suspended')),
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    last_login       TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_batch  ON users(batch_year);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

CREATE TABLE IF NOT EXISTS announcements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    posted_by   INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    location    TEXT NOT NULL,
    starts_at   TEXT NOT NULL,                    -- ISO 'YYYY-MM-DDTHH:MM'
    created_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rsvps (
    event_id    INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (event_id, user_id)
);

CREATE TABLE IF NOT EXISTS jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    company     TEXT NOT NULL,
    location    TEXT,
    job_type    TEXT NOT NULL DEFAULT 'Full-time',
    description TEXT NOT NULL,
    apply_link  TEXT,
    is_open     INTEGER NOT NULL DEFAULT 1,
    posted_by   INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- One-time password reset links, made by a coordinator and shared with the alum.
-- Only a SHA-256 hash of the token is stored, so a copy of the database can't be used to reset passwords.
CREATE TABLE IF NOT EXISTS password_resets (
    token_hash  TEXT PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    expires_at  TEXT NOT NULL,                    -- UTC 'YYYY-MM-DD HH:MM:SS'
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
