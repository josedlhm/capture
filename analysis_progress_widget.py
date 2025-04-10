# analysis_progress_widget.py

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox, 
    QFrame
)
from PySide6.QtCore import Signal, QThread, QObject, Slot, Qt
from config import OUTPUT_DIR
from pipeline_trigger import trigger_pipeline

class BatchAnalysisWorker(QObject):
    """
    Worker to process a batch of captures sequentially.
    Emits progressChanged and finished signals.
    """
    progressChanged = Signal(int, int, int, str)  # (current, total, capture_id, message)
    finished = Signal(list, list)                # (successful capture IDs, failed capture IDs)

    def __init__(self, capture_ids, metadata_service):
        super().__init__()
        self.capture_ids = capture_ids
        self.metadata_service = metadata_service
        self._cancel = False

    def cancel(self):
        self._cancel = True

    @Slot()
    def process(self):
        total = len(self.capture_ids)
        successful = []
        failed = []
        for i, capture_id in enumerate(self.capture_ids):
            if self._cancel:
                break  # Stop before processing the next file

            self.progressChanged.emit(i + 1, total, capture_id, "Starting")
            capture = self.metadata_service.get_capture(capture_id)
            if not capture:
                self.progressChanged.emit(i + 1, total, capture_id, "Not found")
                failed.append(capture_id)
                continue

            filename = capture[1]
            file_path = os.path.join(OUTPUT_DIR, filename)
            metadata = {
                "crop_type": capture[4] or "",
                "variety": capture[5] or "",
                "location": capture[6] or "",
                "username": capture[7] or ""
            }
            try:
                self.metadata_service.update_status_by_id(capture_id, "analysis requested")
                self.progressChanged.emit(i + 1, total, capture_id, "Analyzing")
                # Blocking call; may take a long time
                result = trigger_pipeline(file_path, metadata)
                self.metadata_service.update_status_by_id(capture_id, "analysis complete")
                self.progressChanged.emit(i + 1, total, capture_id, "Completed")
                successful.append(capture_id)
            except Exception as e:
                self.metadata_service.update_status_by_id(capture_id, "analysis failed")
                self.progressChanged.emit(i + 1, total, capture_id, f"Failed: {e}")
                failed.append(capture_id)

        self.finished.emit(successful, failed)


class AnalysisProgressWidget(QWidget):
    """
    A widget to show the progress of a batch analysis, styled as a "card".
    
    Layout:
    - Outer QVBoxLayout with generous margins
    - QFrame card with role="card" for consistent styling
    - Large header label, status label, indeterminate progress bar, red cancel button

    On completion, shows a final message and emits analysisFinished().
    """
    analysisFinished = Signal()  # Signals the main window to return to the list upon finish.

    def __init__(self, capture_ids, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_ids = capture_ids
        self.metadata_service = metadata_service

        # Worker and thread
        self.worker = BatchAnalysisWorker(self.capture_ids, self.metadata_service)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.process)
        self.worker.progressChanged.connect(self.on_progress_changed)
        self.worker.finished.connect(self.on_finished)

        self.init_ui()
        # Indeterminate progress bar
        self.progress_bar.setRange(0, 0)
        self.worker_thread.start()

    def init_ui(self):
        self.setWindowTitle("Analysis In Progress")

        # Outer layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(50, 50, 50, 50)
        outer_layout.setSpacing(30)

        # Create the "card" frame
        card_frame = QFrame()
        card_frame.setProperty("role", "card")  # rely on your global style for QFrame[role="card"]
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(25)
        card_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        self.header_label = QLabel("Analyzing Selected Files")
        self.header_label.setAlignment(Qt.AlignCenter)
        header_font = self.header_label.font()
        header_font.setPointSize(28)
        header_font.setBold(True)
        self.header_label.setFont(header_font)
        card_layout.addWidget(self.header_label, alignment=Qt.AlignCenter)

        # Status label
        self.status_label = QLabel(f"Processing file 0 out of {len(self.capture_ids)}")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = self.status_label.font()
        status_font.setPointSize(20)
        self.status_label.setFont(status_font)
        card_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setTextVisible(False)
        card_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # Cancel button
        self.cancel_button = QPushButton("Cancel Processing")
        cancel_font = self.cancel_button.font()
        cancel_font.setPointSize(18)
        self.cancel_button.setFont(cancel_font)
        self.cancel_button.clicked.connect(self.cancel_processing)
        # Make it red
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #cf3a28;
            }
            QPushButton:pressed {
                background-color: #b53020;
            }
        """)
        card_layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        # Add card to outer layout
        outer_layout.addWidget(card_frame, alignment=Qt.AlignCenter)

      

    @Slot(int, int, int, str)
    def on_progress_changed(self, current, total, capture_id, message):
        # Update textual status only (the progress bar is indeterminate)
        self.status_label.setText(f"Processing file {current} out of {total}: {message}")

    @Slot(list, list)
    def on_finished(self, successful_ids, failed_ids):
        # Clean up
        self.worker_thread.quit()
        self.worker_thread.wait()

        if successful_ids:
            for capture_id in successful_ids:
                self.metadata_service.delete_capture_by_id(capture_id)
            overall_message = f"Analysis successful for {len(successful_ids)} file(s)."
        else:
            overall_message = "Analysis failed for all processed files."

        QMessageBox.information(self, "Analysis Finished", overall_message)
        self.analysisFinished.emit()

    def cancel_processing(self):
        self.worker.cancel()
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Cancelling... (Will stop after the current file)")

