-- FindIt SDSU's authoritative SQLite schema. Use PRAGMA foreign_keys on every connection.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 2 AND 80),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(email) BETWEEN 5 AND 120
               AND email LIKE '%_@_%._%' AND instr(email, ' ') = 0)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(name)) BETWEEN 1 AND 60)
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(name)) BETWEEN 1 AND 80)
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    reporter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    location_id INTEGER NOT NULL REFERENCES locations(id) ON DELETE RESTRICT,
    title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 4 AND 90),
    description TEXT NOT NULL CHECK (length(trim(description)) BETWEEN 12 AND 1200),
    kind TEXT NOT NULL CHECK (kind IN ('Lost', 'Found')),
    status TEXT NOT NULL DEFAULT 'Open'
        CHECK (status IN ('Open', 'Returned') AND (status = 'Open' OR kind = 'Found')),
    report_date TEXT NOT NULL
        CHECK (length(report_date) = 10
               AND report_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
               AND coalesce(date(report_date) = report_date, 0)),
    image_key TEXT CHECK (image_key IS NULL OR image_key IN ('bottle', 'earbuds', 'backpack'))
);

CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE RESTRICT,
    claimant_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    explanation TEXT NOT NULL CHECK (length(trim(explanation)) BETWEEN 15 AND 1000),
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    created_at TEXT NOT NULL DEFAULT (date('now'))
);

CREATE INDEX IF NOT EXISTS idx_items_date ON items(report_date DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_items_kind_category_location
    ON items(kind, category_id, location_id);
CREATE INDEX IF NOT EXISTS idx_claims_item_status ON claims(item_id, status);
CREATE UNIQUE INDEX IF NOT EXISTS one_approved_claim_per_item
    ON claims(item_id) WHERE status = 'Approved';

CREATE TRIGGER IF NOT EXISTS items_start_open
BEFORE INSERT ON items
WHEN NEW.status != 'Open'
BEGIN
    SELECT RAISE(ABORT, 'a new report must start open');
END;

CREATE TRIGGER IF NOT EXISTS items_keep_kind_with_claims
BEFORE UPDATE OF kind ON items
WHEN NEW.kind != OLD.kind
     AND EXISTS (SELECT 1 FROM claims WHERE item_id = OLD.id)
BEGIN
    SELECT RAISE(ABORT, 'an item with claims cannot change kind');
END;

-- A claim starts pending and can only target an open found report.
CREATE TRIGGER IF NOT EXISTS claims_valid_insert
BEFORE INSERT ON claims
WHEN NEW.status != 'Pending'
     OR NOT EXISTS (SELECT 1 FROM items
                    WHERE id = NEW.item_id AND kind = 'Found' AND status = 'Open')
BEGIN
    SELECT RAISE(ABORT, 'claims require an open found item and Pending status');
END;

CREATE TRIGGER IF NOT EXISTS claims_valid_review
BEFORE UPDATE OF status ON claims
WHEN OLD.status != 'Pending'
     OR (NEW.status = 'Approved'
         AND NOT EXISTS (SELECT 1 FROM items
                         WHERE id = NEW.item_id AND kind = 'Found' AND status = 'Open'))
BEGIN
    SELECT RAISE(ABORT, 'claim cannot be reviewed or item is not open');
END;

CREATE TRIGGER IF NOT EXISTS claims_keep_identity
BEFORE UPDATE OF item_id, claimant_id ON claims
WHEN NEW.item_id != OLD.item_id OR NEW.claimant_id != OLD.claimant_id
BEGIN
    SELECT RAISE(ABORT, 'a claim cannot change its item or claimant');
END;

CREATE TRIGGER IF NOT EXISTS claims_keep_approval
BEFORE DELETE ON claims
WHEN OLD.status = 'Approved'
BEGIN
    SELECT RAISE(ABORT, 'an approved claim cannot be deleted');
END;

-- The status change and these updates are one SQLite transaction, even for direct SQL.
CREATE TRIGGER IF NOT EXISTS claims_approved_updates_item
AFTER UPDATE OF status ON claims
WHEN NEW.status = 'Approved'
BEGIN
    UPDATE items SET status = 'Returned' WHERE id = NEW.item_id;
    UPDATE claims SET status = 'Rejected'
    WHERE item_id = NEW.item_id AND id != NEW.id AND status = 'Pending';
END;

CREATE TRIGGER IF NOT EXISTS items_return_requires_approval
BEFORE UPDATE OF status ON items
WHEN NEW.status = 'Returned' AND OLD.status != 'Returned'
     AND NOT EXISTS (SELECT 1 FROM claims
                     WHERE item_id = NEW.id AND status = 'Approved')
BEGIN
    SELECT RAISE(ABORT, 'returning an item requires an approved claim');
END;

CREATE TRIGGER IF NOT EXISTS items_no_reopen_approved
BEFORE UPDATE OF status ON items
WHEN NEW.status = 'Open'
     AND EXISTS (SELECT 1 FROM claims
                 WHERE item_id = NEW.id AND status = 'Approved')
BEGIN
    SELECT RAISE(ABORT, 'an approved item cannot be reopened');
END;
