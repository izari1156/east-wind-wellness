-- East Wind Wellness database schema
-- SQLite is used because it needs no server to install - it is just one
-- file (instance/east_wind_wellness.db) that Python's built-in sqlite3
-- module can read and write directly.

DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone         TEXT,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'user',   -- 'user' or 'admin'
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Herbs and services shown on the "Products and Services" page
CREATE TABLE items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category    TEXT NOT NULL,                    -- 'herb' or 'service'
    name        TEXT NOT NULL,
    tagline     TEXT,
    description TEXT,
    image_file  TEXT,                              -- filename inside static/images/
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE appointments (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    service_name   TEXT NOT NULL,
    full_name      TEXT NOT NULL,
    email          TEXT NOT NULL,
    phone          TEXT NOT NULL,
    preferred_date TEXT NOT NULL,
    preferred_time TEXT NOT NULL,
    notes          TEXT,
    status         TEXT NOT NULL DEFAULT 'pending', -- pending / confirmed / completed / cancelled
    created_at     TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id)
);
