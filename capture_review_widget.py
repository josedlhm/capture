# capture_review_widget.py
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QFrame, QFormLayout, QMessageBox, QApplication
)
from PySide6.QtCore import Signal, Qt

class CaptureReviewWidget(QWidget):
    """
    A widget that displays capture metadata in a card layout and provides
    options to 'Save' or 'Delete' the capture.
    """
    reviewCompleted = Signal(str)

    def __init__(self, capture_file, metadata, parent=None):
        """
        capture_file: The path to the captured file (string).
        metadata: A dict with keys like 'Crop Type', 'Filename', 'Location', etc.
        """
        super().__init__(parent)
        self.capture_file = capture_file
        self.metadata = metadata
        self.init_ui()

    def init_ui(self):
        # Outer layout to center the card in the window
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)
        outer_layout.setContentsMargins(50, 50, 50, 50)

        # Create a QFrame that uses your "card" style (from style.py)
        card_frame = QFrame()
        card_frame.setProperty("role", "card")
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(30)
        card_layout.setContentsMargins(30, 30, 30, 30)

        # Title / Header
        header = QLabel("Review Capture")
        header.setObjectName("Header")  # So it picks up your header style
        header.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(header)

        # Form layout for metadata: key-value pairs
        meta_form = QFormLayout()
        meta_form.setHorizontalSpacing(30)
        meta_form.setVerticalSpacing(12)
        meta_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for key, value in self.metadata.items():
            key_label = QLabel(f"{key}:")
            # Make the key bold/darker
            key_label.setStyleSheet("font-weight: bold; color: #333333;")

            value_label = QLabel(str(value))
            # Slightly lighter color for values, enable word wrap if needed
            value_label.setStyleSheet("color: #555555;")
            value_label.setWordWrap(True)

            meta_form.addRow(key_label, value_label)

        card_layout.addLayout(meta_form)

        # Buttons row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        button_layout.setAlignment(Qt.AlignCenter)

        # Save Capture button
        save_btn = QPushButton("Save Capture")
        save_btn.clicked.connect(self.handle_save)
        button_layout.addWidget(save_btn)

        # Delete Capture button (marked as "danger" to style differently)
        delete_btn = QPushButton("Delete Capture")
        delete_btn.setProperty("role", "danger")
        delete_btn.clicked.connect(self.handle_delete)
        button_layout.addWidget(delete_btn)

        card_layout.addLayout(button_layout)
        outer_layout.addWidget(card_frame, alignment=Qt.AlignCenter)

    def handle_save(self):
        """
        Handle the 'Save Capture' action.
        By default, show a simple message and then signal 'new_capture' or 
        'dashboard' depending on your flow.
        """
        QMessageBox.information(self, "Capture Saved", "Capture saved successfully!")
        self.finish_review("dashboard") 

    def handle_delete(self):
        """
        Confirmation dialog before deleting the capture.
        """
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this capture?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.finish_review("delete")

    def finish_review(self, action):
        """
        Emit the final decision so the main window can navigate.
        """
        self.reviewCompleted.emit(action)

