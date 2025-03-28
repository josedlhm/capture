# main.py
import sys
from PySide6.QtWidgets import QApplication
from capture_service import CaptureService
from metadata_service import MetadataService
from config import OUTPUT_DIR, DB_PATH
from main_window import MainWindow
import qt_themes

def main():
    cap_service = CaptureService(OUTPUT_DIR)
    meta_service = MetadataService(DB_PATH)
    app = QApplication(sys.argv)
    qt_themes.set_theme('blender')
    window = MainWindow(cap_service, meta_service)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()