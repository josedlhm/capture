import sys
import os
from PySide6 import QtWidgets
from crop_camera_app import CropCameraApp
from capture_service import CaptureService
from metadata_service import MetadataService
from config import OUTPUT_DIR, DB_PATH

def main():

    cap_service = CaptureService(OUTPUT_DIR)
    meta_service = MetadataService(DB_PATH)
    
    app = QtWidgets.QApplication(sys.argv)
    window = CropCameraApp(cap_service, meta_service)
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()