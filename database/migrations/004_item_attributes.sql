-- Nullable for earlier reports; new reports collect an explicit item type.
ALTER TABLE items ADD COLUMN item_type TEXT CHECK (item_type IS NULL OR item_type IN
    ('Smartphone','Earbuds','Laptop','Backpack','Water Bottle','Keys','Wallet','Notebook','Clothing','Other'));
ALTER TABLE items ADD COLUMN brand TEXT CHECK (brand IS NULL OR length(trim(brand)) BETWEEN 1 AND 60);
ALTER TABLE items ADD COLUMN model TEXT CHECK (model IS NULL OR length(trim(model)) BETWEEN 1 AND 80);
ALTER TABLE items ADD COLUMN color TEXT CHECK (color IS NULL OR length(trim(color)) BETWEEN 1 AND 30);
CREATE INDEX idx_items_match_type ON items(kind, status, category_id, item_type, report_date);
