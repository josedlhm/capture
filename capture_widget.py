# capture_widget.py
import os
import cv2
import logging
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets
import pyzed.sl as sl

class CaptureWidget(QtWidgets.QWidget):
    # Define a custom signal that sends the capture file path and metadata as a dict.
    captureCompleted = QtCore.Signal(str, dict)
    
    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service
        self.current_capture_file = None

        # Apply a consistent dark theme.
        self.setStyleSheet("""
            QWidget { background-color: #2c2c2c; }
            QPushButton { font-size: 20px; padding: 10px; background-color: #444444; color: white; border: 2px solid #666; border-radius: 5px; }
            QPushButton:hover { background-color: #555555; }
            QLabel { color: white; font-size: 18px; }
        """)

        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Video display label.
        self.video_label = QtWidgets.QLabel("Initializing ZED Camera...", self)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.video_label, stretch=1)

        # "REC" indicator overlay.
        self.rec_label = QtWidgets.QLabel("REC", self.video_label)
        self.rec_label.setStyleSheet("color: red; font-size: 28px; font-weight: bold;")
        self.rec_label.hide()
        self.rec_label.move(10, 10)
        self.rec_label.raise_()

        # Control buttons.
        self.button_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(self.button_layout)
        self.start_button = QtWidgets.QPushButton("Start")
        self.start_button.clicked.connect(self.start_recording)
        self.button_layout.addWidget(self.start_button)
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_recording)
        self.button_layout.addWidget(self.stop_button)

        # ZED camera setup.
        self.cam = self.capture_service.cam
        self.image_zed = sl.Mat()
        self.runtime = sl.RuntimeParameters()

        # Timer to update the video feed (~60 FPS).
        self.timer = QtCore.QTimer(self)
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
            self.current_capture_file = self.capture_service.start_capture()
            self.rec_label.show()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def stop_recording(self):
        try:
            self.capture_service.stop_capture()
            self.rec_label.hide()
            if self.current_capture_file:
                filename = os.path.basename(self.current_capture_file)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Assume self.parent().current_capture_options holds the options from CaptureOptionsWidget.
                # Alternatively, pass them via signal or store in a global or shared object.
                options = getattr(self, 'capture_options', {})  # A dictionary with keys: capture_type, variety, location.
                
                # Save extended metadata.
                self.metadata_service.add_capture(
                    filename, timestamp, "captured",
                    capture_type=options.get("capture_type"),
                    variety=options.get("variety"),
                    location=options.get("location")
                )
                
                metadata = {
                    "Filename": filename,
                    "Timestamp": timestamp,
                    "Capture Type": options.get("capture_type", "N/A"),
                    "Variety": options.get("variety", "N/A"),
                    "Location": options.get("location", "N/A")
                }
                # Emit the captureCompleted signal with the extended metadata.
                self.captureCompleted.emit(self.current_capture_file, metadata)
                logging.info("Capture completed and metadata recorded for: %s", filename)
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
