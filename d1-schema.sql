-- PastForward community data on Cloudflare D1 (SQLite).
-- Run once in Cloudflare → Workers & Pages → D1 → pastforward → Console.
CREATE TABLE IF NOT EXISTS votes (
  rhyme_id   TEXT    NOT NULL CHECK (length(rhyme_id) BETWEEN 1 AND 40),
  device_id  TEXT    NOT NULL CHECK (length(device_id) = 36),
  vote       INTEGER NOT NULL CHECK (vote IN (-1, 1)),
  created_at TEXT    NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (rhyme_id, device_id)
);
CREATE TABLE IF NOT EXISTS puzzle_results (
  day        INTEGER NOT NULL CHECK (day BETWEEN 1 AND 100000),
  device_id  TEXT    NOT NULL CHECK (length(device_id) = 36),
  score      INTEGER NOT NULL CHECK (score BETWEEN 0 AND 3),
  created_at TEXT    NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (day, device_id)
);

-- Ask PastForward (subscribers). The API creates these by itself on first use; listed here for reference.
CREATE TABLE IF NOT EXISTS ask_licences (key_hash TEXT PRIMARY KEY, ok INTEGER NOT NULL, status TEXT, plan TEXT, expires_at TEXT, checked_at INTEGER NOT NULL, last_ok_at INTEGER);
CREATE TABLE IF NOT EXISTS ask_usage (key_hash TEXT NOT NULL, month TEXT NOT NULL, used INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (key_hash, month));
CREATE TABLE IF NOT EXISTS ask_spend (day TEXT PRIMARY KEY, micro INTEGER NOT NULL DEFAULT 0, calls INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS ask_cache (q_hash TEXT PRIMARY KEY, q TEXT NOT NULL, answer TEXT NOT NULL, created_at INTEGER NOT NULL, hits INTEGER NOT NULL DEFAULT 0);
