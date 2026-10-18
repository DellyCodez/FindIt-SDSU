-- Nullable columns leave legacy reports unchanged.
ALTER TABLE items ADD COLUMN item_type TEXT CHECK (item_type IS NULL OR length(trim(item_type)) BETWEEN 2 AND 40);
ALTER TABLE items ADD COLUMN brand TEXT CHECK (brand IS NULL OR length(trim(brand)) BETWEEN 1 AND 60);
ALTER TABLE items ADD COLUMN model TEXT CHECK (model IS NULL OR length(trim(model)) BETWEEN 1 AND 60);
ALTER TABLE items ADD COLUMN primary_color TEXT CHECK (primary_color IS NULL OR length(trim(primary_color)) BETWEEN 2 AND 40);
ALTER TABLE items ADD COLUMN distinguishing_features TEXT CHECK (distinguishing_features IS NULL OR length(trim(distinguishing_features)) BETWEEN 3 AND 300);
CREATE INDEX IF NOT EXISTS idx_items_type_candidates ON items(kind, status, category_id, item_type, report_date);
