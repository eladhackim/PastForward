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
