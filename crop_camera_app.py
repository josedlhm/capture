import sys
import os
import cv2
import numpy as np
import logging
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets
import pyzed.sl as sl
from capture_service import CaptureService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CropCameraApp(QtWidgets.QMainWindow):
    def __init__(self, capture_service, metadata_service):
        super(CropCameraApp, self).__init__()
        self.setWindowTitle("Crop Camera App")
        self.resize(800, 600)
        self.capture_service = capture_service
        self.metadata_service = metadata_service
        self.current_capture_file = None  # Will hold the file path for the current capture session

        # Simple dark-themed style.
        stylesheet = """
        QMainWindow { background-color: #2c2c2c; }
        QPushButton { font-size: 20px; padding: 10px; background-color: #444444; color: white; border: 2px solid #666; border-radius: 5px; }
        QPushButton:hover { background-color: #555555; }
        QLabel { color: white; font-size: 18px; }
        """
        self.setStyleSheet(stylesheet)

        # Set up central widget and layout.
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Video display.
        self.video_label = QtWidgets.QLabel("Initializing ZED Camera...", self)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.video_label, stretch=1)

        # "REC" indicator overlay.
        self.rec_label = QtWidgets.QLabel("REC", self.video_label)
        self.rec_label.setStyleSheet("color: red; font-size: 28px; font-weight: bold;")
        self.rec_label.hide()
        self.rec_label.move(10, 10)
        self.rec_label.raise_()

        # Control buttons.
        self.button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.clicked.connect(self.start_recording)
        self.button_layout.addWidget(self.start_button)
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_recording)
        self.button_layout.addWidget(self.stop_button)
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.exit_button)

        # Use the camera from the capture service.
        self.cam = self.capture_service.cam
        self.image_zed = sl.Mat()
        self.runtime = sl.RuntimeParameters()

        # Timer for updating the video feed (~60 FPS).
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16)

    def update_frame(self):
        if self.cam.grab(self.runtime) == sl.ERROR_CODE.SUCCESS:
            self.cam.retrieve_image(self.image_zed, sl.VIEW.LEFT)
            frame = self.image_zed.get_data()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = rgb_frame.shape
            bytes_per_line = channels * width
            q_img = QtGui.QImage(rgb_frame.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(q_img)
            pixmap = pixmap.scaled(self.video_label.size(), QtCore.Qt.KeepAspectRatio)
            self.video_label.setPixmap(pixmap)

    def start_recording(self):
        try:
            # Assuming start_capture() returns the file path.
            self.current_capture_file = self.capture_service.start_capture()
            self.rec_label.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def stop_recording(self):
        try:
            self.capture_service.stop_capture()
            self.rec_label.hide()
            if self.current_capture_file:
                # Record metadata upon stopping.
                filename = os.path.basename(self.current_capture_file)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.metadata_service.add_capture(filename, timestamp, "captured")
                logging.info("Metadata recorded for capture: %s", filename)
                # Clear the current capture file.
                self.current_capture_file = None
            else:
                logging.warning("No current capture file to record metadata for.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def closeEvent(self, event):
        if self.capture_service.recording:
            self.capture_service.stop_capture()
        self.capture_service.close_camera()
        event.accept()
