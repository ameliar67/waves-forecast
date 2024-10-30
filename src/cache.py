import datetime
import sqlite3

class Cache:
    def __init__(self, cache_file: str) -> None:
        self.conn = sqlite3.connect(cache_file, detect_types=sqlite3.PARSE_COLNAMES, check_same_thread=False)

    def migrate(self) -> None:
        with open("schema.sql") as f:
            self.conn.executescript(f.read())

    def get_item(self, key):
        row = self.conn.execute("SELECT * FROM cache WHERE key = ?", [key]).fetchone()
        if row is None or row[2] < datetime.datetime.now().day:
            return None

        return row[1]


    def set_item(self, key, value, expiry, wave_height):
        self.conn.execute("INSERT INTO cache (key, value, expiry, wave_height) VALUES (?, ?, ?, ?)", [key, value, expiry, wave_height])

    def close(self):
        self.conn.close()
