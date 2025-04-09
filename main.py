# main.py

import sys
from PySide6.QtWidgets import QApplication
import qt_themes
import requests

from config import OUTPUT_DIR, DB_PATH
from capture_service import CaptureService
from metadata_service import MetadataService
from main_window import MainWindow
from style import load_stylesheet  # Import the global stylesheet

def init_services():
    """Initialize and return core services."""
    capture_service = CaptureService(OUTPUT_DIR)
    metadata_service = MetadataService(DB_PATH)
    return capture_service, metadata_service

def run_app():
    """Entry point of the application."""
    app = QApplication(sys.argv)
    
    # Set GitHub Light theme (background colors, etc.) first
    qt_themes.set_theme('github_light')
    
    # Apply the agritech global stylesheet for tablet use
    app.setStyleSheet(load_stylesheet())
    
    capture_service, metadata_service = init_services()
    window = MainWindow(capture_service, metadata_service)
    window.showFullScreen()  # or window.show() if you prefer windowed mode
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
