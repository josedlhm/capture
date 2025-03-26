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
                status TEXT
            )
        """)
        self.conn.commit()
    
    def add_capture(self, filename, timestamp, status="captured"):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO captures (filename, timestamp, status)
            VALUES (?, ?, ?)
        """, (filename, timestamp, status))
        self.conn.commit()
    
    def update_status(self, filename, status):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE captures SET status = ? WHERE filename = ?
        """, (status, filename))
        self.conn.commit()
    
    def list_captures(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, filename, timestamp, status FROM captures")
        rows = cursor.fetchall()
        return rows

    def get_capture(self, capture_id):
        """
        Retrieve a single capture record by its ID.
        Returns a tuple (id, filename, timestamp, status) or None if not found.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, filename, timestamp, status FROM captures WHERE id = ?", (capture_id,))
        row = cursor.fetchone()
        return row
