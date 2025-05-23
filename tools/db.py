import sqlite3
from datetime import datetime

class AttackLogger:
    def __init__(self, db_path="offensivepython/attacks.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            port INTEGER NOT NULL,
            method TEXT NOT NULL,
            pps INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        );
        """)
        self.conn.commit()

    def log_attack(self, target, port, method, pps, duration):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO attacks (target, port, method, pps, duration, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (target, port, method, pps, duration, datetime.utcnow().isoformat()))
        self.conn.commit()

    def close(self):
        self.conn.close()
