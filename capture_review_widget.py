import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal, Qt

class CaptureReviewWidget(QWidget):
    # Signal that communicates the user's final decision.
    # It will send one of the following strings: "delete", "new_capture", or "dashboard".
    reviewCompleted = Signal(str)

    def __init__(self, capture_file, metadata, parent=None):
        """
        capture_file: The path to the captured file.
        metadata: A dictionary with metadata (e.g., timestamp, capture type, variety, location).
        """
        super().__init__(parent)
        self.capture_file = capture_file
        self.metadata = metadata
        self.setStyleSheet("""
            QWidget { background-color: #2c2c2c; }
            QLabel { color: white; font-size: 18px; }
            QPushButton { font-size: 20px; padding: 10px; background-color: #444444; color: white; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #555555; }
        """)
        self.init_ui()

    def init_ui(self):
        # Create and save the main layout.
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignCenter)

        # Header
        header = QLabel("Review Capture")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 28px; font-weight: bold;")
        self.layout_main.addWidget(header)

        # Instead of a thumbnail, show a message.
        no_thumbnail_label = QLabel("No thumbnail available")
        no_thumbnail_label.setAlignment(Qt.AlignCenter)
        self.layout_main.addWidget(no_thumbnail_label)

        # Display metadata.
        meta_info = "\n".join(f"{k}: {v}" for k, v in self.metadata.items())
        meta_label = QLabel(meta_info)
        meta_label.setAlignment(Qt.AlignCenter)
        self.layout_main.addWidget(meta_label)

        # Action buttons: Save or Delete.
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Capture")
        save_btn.clicked.connect(self.handle_save)
        button_layout.addWidget(save_btn)

        delete_btn = QPushButton("Delete Capture")
        delete_btn.clicked.connect(lambda: self.finish_review("delete"))
        button_layout.addWidget(delete_btn)

        self.layout_main.addLayout(button_layout)

    def clear_layout(self, layout):
        # Recursively remove all items from the layout.
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def handle_save(self):
        # Clear the current main layout.
        self.clear_layout(self.layout_main)
        
        # Reuse the same layout to add the confirmation message and follow-up options.
        confirmation_label = QLabel("Capture saved successfully!")
        confirmation_label.setAlignment(Qt.AlignCenter)
        self.layout_main.addWidget(confirmation_label)

        # Create a horizontal layout for the follow-up buttons.
        button_layout = QHBoxLayout()
        new_capture_btn = QPushButton("Take New Capture")
        new_capture_btn.clicked.connect(lambda: self.finish_review("new_capture"))
        button_layout.addWidget(new_capture_btn)

        dashboard_btn = QPushButton("Return to Dashboard")
        dashboard_btn.clicked.connect(lambda: self.finish_review("dashboard"))
        button_layout.addWidget(dashboard_btn)

        self.layout_main.addLayout(button_layout)

    def finish_review(self, action):
        # Emit the final decision.
        print(f"User chose to {action}")
        self.reviewCompleted.emit(action)
