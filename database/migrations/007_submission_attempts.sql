-- Shared rate limits for public form submissions. Store only a keyed IP digest.
CREATE TABLE IF NOT EXISTS submission_attempts (
    id INTEGER PRIMARY KEY,
    action TEXT NOT NULL CHECK (action IN ('report', 'claim', 'login')),
    actor_key TEXT NOT NULL CHECK (length(actor_key) = 64),
    created_at INTEGER NOT NULL CHECK (created_at > 0)
);

CREATE INDEX IF NOT EXISTS idx_submission_attempts_window
    ON submission_attempts(action, actor_key, created_at);
