-- Keep the public distinguishing details used by the published v4 application.
ALTER TABLE items ADD COLUMN distinguishing_features TEXT
    CHECK (distinguishing_features IS NULL OR length(trim(distinguishing_features)) BETWEEN 3 AND 300);
