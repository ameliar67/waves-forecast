import datetime
import sqlite3

class Cache:
    def __init__(self, cache_file: str) -> None:
        self.conn = sqlite3.connect(cache_file, detect_types=sqlite3.PARSE_COLNAMES, check_same_thread=False)

    def migrate(self) -> None:
        with open("schema.sql") as f:
            self.conn.executescript(f.read())

    # TODO: row[n] relies on implicit ordering of columns in SELECT * result
    def get_item(self, key):
        row = self.conn.execute("SELECT value, expiry FROM cache WHERE key = ?", [key]).fetchone()
        if row is None:
            return None

        if row[1] < datetime.datetime.now().day:
            self.conn.execute("DELETE FROM cache WHERE key = ?;", [key])
            return None

        return row[0]

    def set_item(self, key, value, expiry):
        self.conn.execute("INSERT INTO cache (key, value, expiry) VALUES (?, ?, ?)", [key, value, expiry])
        self.conn.commit()

    def close(self):
        self.conn.close()
