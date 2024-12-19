import datetime
import sqlite3


class Cache:
    def __init__(self, cache_file: str) -> None:
        self.conn = sqlite3.connect(
            cache_file, detect_types=sqlite3.PARSE_COLNAMES, check_same_thread=False
        )

    def migrate(self) -> None:
        with open("schema.sql") as f:
            self.conn.executescript(f.read())

    def get_item(self, key) -> None:
        row = self.conn.execute(
            "SELECT chart, expiry, average_wave_height FROM cache WHERE key = ?", [key]
        ).fetchone()
        
        if row is None:
            return None

        if row[1] < datetime.datetime.now().day:
            self.conn.execute("DELETE FROM cache WHERE key = ?;", [key])
            return None

        result = {
            'chart': row[0],
            'wave_height': row[2]
        }
        return result

    def set_item(self, key, chart, average_wave_height, expiry) -> None:
        self.conn.execute(
            "INSERT INTO cache (key, chart, average_wave_height, expiry) VALUES (?, ?, ?, ?)",
            [key, chart, average_wave_height, expiry],
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
