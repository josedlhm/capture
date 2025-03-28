# main.py
import sys
from PySide6.QtWidgets import QApplication
from capture_service import CaptureService
from metadata_service import MetadataService
from config import OUTPUT_DIR, DB_PATH
from main_window import MainWindow

def main():
    cap_service = CaptureService(OUTPUT_DIR)
    meta_service = MetadataService(DB_PATH)
    app = QApplication(sys.argv)
    window = MainWindow(cap_service, meta_service)
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()