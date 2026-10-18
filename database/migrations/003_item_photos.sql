-- Add photo associations without changing any existing report or claim.
CREATE TABLE item_photos (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL UNIQUE
        CHECK (length(file_name) = 37 AND substr(file_name, -5) = '.webp'),
    position INTEGER NOT NULL CHECK (position BETWEEN 1 AND 3),
    mime_type TEXT NOT NULL CHECK (mime_type = 'image/webp'),
    width INTEGER NOT NULL CHECK (width BETWEEN 1 AND 1600),
    height INTEGER NOT NULL CHECK (height BETWEEN 1 AND 1600),
    byte_count INTEGER NOT NULL CHECK (byte_count BETWEEN 1 AND 8388608),
    UNIQUE (item_id, position)
);
