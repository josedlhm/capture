# metadata_service.py
import sqlite3

class MetadataService:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                timestamp TEXT,
                status TEXT,
                crop_type TEXT,
                variety TEXT,
                location TEXT,
                username TEXT
            )
        """)
        self.conn.commit()
    
    def add_capture(
        self,
        filename,
        timestamp,
        status="captured",
        crop_type=None,
        variety=None,
        location=None,
        username=None
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO captures 
            (filename, timestamp, status, crop_type, variety, location, username)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (filename, timestamp, status, crop_type, variety, location, username)
        )
        self.conn.commit()

    def update_status(self, filename, status):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE captures SET status = ? WHERE filename = ?
        """, (status, filename))
        self.conn.commit()

    def list_captures(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, filename, timestamp, status, 
                   crop_type, variety, location, username
            FROM captures
        """)
        rows = cursor.fetchall()
        return rows

    def get_capture(self, capture_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, filename, timestamp, status,
                   crop_type, variety, location, username
            FROM captures
            WHERE id = ?
        """, (capture_id,))
        row = cursor.fetchone()
        return row

    def delete_capture_by_id(self, capture_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM captures WHERE id = ?
        """, (capture_id,))
        self.conn.commit()

    def update_status_by_id(self, capture_id, new_status):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE captures SET status = ? WHERE id = ?
        """, (new_status, capture_id))
        self.conn.commit()
