-- Add the candidate lookup index without rebuilding tables or touching records.
CREATE INDEX IF NOT EXISTS idx_items_match_candidates
    ON items(kind, status, category_id, report_date);
