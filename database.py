import sqlite3
import os

DB_NAME = "tweakos.db"

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS authorized_users (
                user_id INTEGER PRIMARY KEY
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                cooldown REAL,
                messages_sent INTEGER,
                start_time TEXT,
                end_time TEXT,
                status TEXT
            )
        """)
        self.conn.commit()
        # Владелец (первый авторизованный) по умолчанию 0, будет добавлен при настройке
        self._init_defaults()

    def _init_defaults(self):
        # Добавляем стандартные настройки, если отсутствуют
        defaults = {
            "api_id": "",
            "api_hash": "",
            "phone": "",
            "bot_token": "8660327115:AAEF4zEvki-q4d6_6QAU80FTlX21iEqKiMM",
            "default_cooldown": "0.6"
        }
        for k, v in defaults.items():
            self.cursor.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", (k, v))
        self.conn.commit()

    def get_setting(self, key):
        self.cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def is_configured(self):
        api_id = self.get_setting("api_id")
        api_hash = self.get_setting("api_hash")
        phone = self.get_setting("phone")
        return all([api_id, api_hash, phone])

    def add_authorized_user(self, user_id):
        self.cursor.execute("INSERT OR IGNORE INTO authorized_users VALUES (?)", (user_id,))
        self.conn.commit()

    def remove_authorized_user(self, user_id):
        self.cursor.execute("DELETE FROM authorized_users WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def is_authorized(self, user_id):
        self.cursor.execute("SELECT 1 FROM authorized_users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone() is not None

    def get_all_authorized(self):
        self.cursor.execute("SELECT user_id FROM authorized_users")
        return [row[0] for row in self.cursor.fetchall()]

    def log_attack(self, target, cooldown, messages_sent, start_time, end_time, status):
        self.cursor.execute("""
            INSERT INTO attack_logs (target, cooldown, messages_sent, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (target, cooldown, messages_sent, start_time, end_time, status))
        self.conn.commit()

    def close(self):
        self.conn.close()
