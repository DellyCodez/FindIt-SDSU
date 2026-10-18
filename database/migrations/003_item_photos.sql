-- Add photos without rebuilding or changing existing reports and claims.
CREATE TABLE item_photos (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position BETWEEN 1 AND 3),
    filename TEXT NOT NULL UNIQUE
        CHECK (length(filename) = 37 AND filename GLOB '[0-9a-f]*.webp'),
    width INTEGER NOT NULL CHECK (width BETWEEN 1 AND 1800),
    height INTEGER NOT NULL CHECK (height BETWEEN 1 AND 1800),
    byte_size INTEGER NOT NULL CHECK (byte_size > 0),
    UNIQUE (item_id, position)
);
CREATE INDEX idx_item_photos_item ON item_photos(item_id, position);
