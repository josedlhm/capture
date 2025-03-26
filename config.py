import os

# Define a common storage directory.
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "new_captures_gui")

# Define the database path within that directory.
DB_PATH = os.path.join(OUTPUT_DIR, "captures.db")