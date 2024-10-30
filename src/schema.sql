CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value BLOB NOT NULL,
    expiry TIMESTAMP NOT NULL,
    wave_height INT NOT NULL
);
