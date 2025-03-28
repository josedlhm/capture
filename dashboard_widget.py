# dashboard_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal, Qt

class DashboardWidget(QWidget):
    # Signal to request navigation: 1 for New Capture, 2 for View Captures.
    navigationRequested = Signal(int)

    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service

        # Use a dark theme with larger fonts and padding for touch.
        self.setStyleSheet("""
            QWidget {
                background-color: #323232;
            }
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                font-size: 24px;         /* Larger font for touch-friendly text */
                padding: 20px;           /* Increased padding for larger touch targets */
                border: none;
                border-radius: 8px;      /* Rounded corners for a modern look */
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 60, 60, 60)  # More margin around the edges
        layout.setSpacing(30)

        # Container for the two action buttons
        button_container = QHBoxLayout()
        button_container.setSpacing(60)
        button_container.setAlignment(Qt.AlignCenter)

        new_capture_btn = QPushButton("Take a New Capture")
        new_capture_btn.setMinimumWidth(300)   # Larger button for tablet use
        new_capture_btn.setMinimumHeight(100)
        new_capture_btn.clicked.connect(lambda: self.navigationRequested.emit(1))
        button_container.addWidget(new_capture_btn)

        view_captures_btn = QPushButton("View Captures")
        view_captures_btn.setMinimumWidth(300)
        view_captures_btn.setMinimumHeight(100)
        view_captures_btn.clicked.connect(lambda: self.navigationRequested.emit(3))
        button_container.addWidget(view_captures_btn)

        layout.addLayout(button_container)
