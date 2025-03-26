import sys
import os
from PySide6 import QtWidgets
from crop_camera_app import CropCameraApp
from capture_service import CaptureService
from metadata_service import MetadataService

def main():
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "new_captures_gui")
    db_path = os.path.join(os.path.expanduser("~"), "Desktop", "captures.db")
    
    cap_service = CaptureService(output_dir)
    meta_service = MetadataService(db_path)
    
    app = QtWidgets.QApplication(sys.argv)
    window = CropCameraApp(cap_service, meta_service)
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()