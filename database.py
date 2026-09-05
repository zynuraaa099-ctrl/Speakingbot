"""
Ma'lumotlar bazasi bilan ishlash uchun yordamchi modul.
SQLite ishlatiladi - alohida server o'rnatish shart emas, bitta fayl yetarli.
"""
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "speaking_bot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Bot birinchi marta ishga tushganda kerakli jadvallarni yaratadi."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            group_name TEXT NOT NULL,
            username TEXT,
            registered_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sent_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES students(user_id)
        )
    """)
    conn.commit()
    conn.close()


def is_registered(user_id: int) -> bool:
    conn = get_connection()
    row = conn.execute("SELECT 1 FROM students WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row is not None


def register_student(user_id: int, full_name: str, group_name: str, username: str | None):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO students (user_id, full_name, group_name, username, registered_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, full_name, group_name, username, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_student(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def log_submission(user_id: int):
    conn = get_connection()
    conn.execute(
        "INSERT INTO submissions (user_id, sent_at) VALUES (?, ?)",
        (user_id, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY group_name, full_name").fetchall()
    conn.close()
    return rows


def get_report(days: int):
    """
    Berilgan kun oralig'ida har bir o'quvchi nechta video yuborganini qaytaradi.
    days=1  -> bugungi hisobot
    days=7  -> haftalik hisobot
    Ro'yxatdan o'tgan, lekin hech narsa yubormagan o'quvchilar ham 0 bilan ko'rsatiladi.
    """
    since = (datetime.now() - timedelta(days=days)).isoformat()
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT s.full_name, s.group_name, s.username,
               COUNT(sub.id) AS cnt
        FROM students s
        LEFT JOIN submissions sub
               ON sub.user_id = s.user_id AND sub.sent_at >= ?
        GROUP BY s.user_id
        ORDER BY s.group_name, cnt DESC, s.full_name
        """,
        (since,),
    ).fetchall()
    conn.close()
    return rows
