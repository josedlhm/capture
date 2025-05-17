# capture_widget.py

import os
import logging
from datetime import datetime
from PySide6 import QtCore, QtWidgets

class CaptureWidget(QtWidgets.QWidget):
    """
    Headless capture widget: no video preview.
    Just Start/Stop → prompt once → save metadata → show review.
    """
    captureCompleted = QtCore.Signal(str, dict)

    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service  = capture_service
        self.metadata_service = metadata_service
        self._preexisting     = set()

        layout = QtWidgets.QVBoxLayout(self)

        # Just a label instead of video
        self.status_label = QtWidgets.QLabel("Preview disabled", self)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_label, stretch=1)

        btns = QtWidgets.QHBoxLayout()
        layout.addLayout(btns)
        self.start_button = QtWidgets.QPushButton("Start Recording")
        self.stop_button  = QtWidgets.QPushButton("Stop Recording")
        btns.addWidget(self.start_button)
        btns.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)

    def start_recording(self):
        # snapshot existing files
        self._preexisting = set(os.listdir(self.capture_service.output_dir))

        if not self.capture_service.start_capture():
            QtWidgets.QMessageBox.warning(self, "Start Failed", "Could not start recording.")
            return

        self.status_label.setText("Recording…")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        logging.info("Recording started; preexisting=%s", self._preexisting)

    def stop_recording(self):
        self.capture_service.stop_capture()
        self.status_label.setText("Processing capture…")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        # find new files
        out_dir = self.capture_service.output_dir
        after = set(os.listdir(out_dir))
        new_files = sorted(after - self._preexisting)
        new_files = [f for f in new_files if f.lower().endswith((".svo", ".svo2"))]

        if not new_files:
            QtWidgets.QMessageBox.information(self, "No Capture", "No new capture files found.")
            self.status_label.setText("Preview disabled")
            return

        # single “Save?” prompt
        reply = QtWidgets.QMessageBox.question(
            self,
            "Save Capture",
            "Do you want to save this capture?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )

        if reply == QtWidgets.QMessageBox.Yes:
            opts = getattr(self, "capture_options", {})
            first_meta = None

            for idx, fname in enumerate(new_files):
                ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.metadata_service.add_capture(
                    fname, ts_str, "captured",
                    crop_type=opts.get("crop_type"),
                    variety=opts.get("variety"),
                    location=opts.get("location"),
                    username=opts.get("username")
                )

                if idx == 0:
                    first_meta = {
                        "Filename":  fname,
                        "Timestamp": ts_str,
                        "Crop Type": opts.get("crop_type","N/A"),
                        "Variety":   opts.get("variety","N/A"),
                        "Location":  opts.get("location","N/A"),
                        "Username":  opts.get("username","N/A"),
                    }

            # emit review for the first file
            if first_meta:
                self.captureCompleted.emit(
                    os.path.join(out_dir, new_files[0]),
                    first_meta
                )
                logging.info("Emitted captureCompleted for %s", new_files[0])

        else:
            logging.info("User declined to save capture: %s", new_files)

        self.status_label.setText("Preview disabled")

    def closeEvent(self, event):
        if getattr(self.capture_service, "recording", False):
            self.capture_service.stop_capture()
        self.capture_service.close_camera()
        event.accept()
