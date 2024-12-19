CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    chart BLOB NOT NULL,
    expiry TIMESTAMP NOT NULL,
    average_wave_height INT NOT NULL
);
