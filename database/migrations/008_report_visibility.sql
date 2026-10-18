-- Existing reports stay public. Moderators can hide a report without deleting its history.
ALTER TABLE items ADD COLUMN visibility TEXT NOT NULL DEFAULT 'Visible'
    CHECK (visibility IN ('Visible', 'Hidden'));

CREATE INDEX IF NOT EXISTS idx_items_visibility_date
    ON items(visibility, report_date DESC, id DESC);
