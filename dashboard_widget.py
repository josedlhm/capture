from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt

class DashboardWidget(QWidget):
    navigationRequested = Signal(int)

    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service

       

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(40)

        # Optional title
        header = QLabel("📸 Capture Dashboard")
        header.setObjectName("Header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Buttons layout
        button_container = QHBoxLayout()
        button_container.setSpacing(60)
        button_container.setAlignment(Qt.AlignCenter)

        new_capture_btn = QPushButton("📷  Take a New Capture")
        new_capture_btn.clicked.connect(lambda: self.navigationRequested.emit(2))
        button_container.addWidget(new_capture_btn)

        view_captures_btn = QPushButton("🗂️  View Captures")
        view_captures_btn.clicked.connect(lambda: self.navigationRequested.emit(4))
        button_container.addWidget(view_captures_btn)

        layout.addLayout(button_container)
