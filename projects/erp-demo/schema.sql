-- ERP Demo Schema — GEO Agency Quote Tracker + Client Log
-- SQLite, all KRW values as INTEGER (no decimals)

CREATE TABLE IF NOT EXISTS clients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    business_name TEXT NOT NULL,
    phone         TEXT,
    email         TEXT,
    kakao_id      TEXT,
    website       TEXT,
    status        TEXT DEFAULT 'lead',
    source        TEXT,
    geo_score     INTEGER,
    notes         TEXT,
    created_at    TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at    TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS interactions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id  INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    type       TEXT NOT NULL,
    content    TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS quotes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id    INTEGER NOT NULL REFERENCES clients(id),
    quote_number TEXT UNIQUE NOT NULL,
    title        TEXT NOT NULL,
    status       TEXT DEFAULT 'draft',
    valid_until  TEXT,
    notes        TEXT,
    created_at   TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at   TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS quote_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id    INTEGER NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    quantity    INTEGER DEFAULT 1,
    unit_price  INTEGER NOT NULL,
    sort_order  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS invoices (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id       INTEGER REFERENCES quotes(id),
    client_id      INTEGER NOT NULL REFERENCES clients(id),
    invoice_number TEXT UNIQUE NOT NULL,
    total_amount   INTEGER NOT NULL,
    status         TEXT DEFAULT 'unpaid',
    issued_at      TEXT DEFAULT (datetime('now', 'localtime')),
    due_date       TEXT,
    paid_at        TEXT
);

CREATE TABLE IF NOT EXISTS message_queue (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id  INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    type       TEXT NOT NULL,
    channel    TEXT DEFAULT 'kakao',
    message    TEXT NOT NULL,
    status     TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
