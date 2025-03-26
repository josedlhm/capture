# storage_service.py
import os

class StorageService:
    def __init__(self, storage_dir):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def list_captures(self):
        """List all SVO2 capture files in the storage directory."""
        files = [os.path.join(self.storage_dir, f) for f in os.listdir(self.storage_dir) if f.endswith(".svo2")]
        return files
    
    def get_capture(self, filename):
        """Return the full path of a capture file, if it exists."""
        filepath = os.path.join(self.storage_dir, filename)
        return filepath if os.path.exists(filepath) else None
    
    def store_capture(self, capture_path):
        """For a local system the file is already stored; this function could be used to copy or process the file as needed."""
        return capture_path