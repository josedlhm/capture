# dashboard_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal

class DashboardWidget(QWidget):
    navigationRequested = Signal(int)
    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service
        self.init_ui()

    def init_ui(self):
        # Apply dark theme styling.
        self.setStyleSheet("""
            QWidget { background-color: #2c2c2c; }
            QLabel { color: white; }
            QPushButton { font-size: 20px; padding: 15px; background-color: #444444; color: white; border: none; border-radius: 5px; }
            QPushButton:hover { background-color: #555555; }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title.
        title = QLabel("Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold;")
        layout.addWidget(title)

        # Subtitle.
        subtitle = QLabel("Select an action:")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18px;")
        layout.addWidget(subtitle)

        layout.addSpacing(50)

        # Buttons layout.
        btn_layout = QHBoxLayout()
        new_capture_btn = QPushButton("Take a New Capture")
        new_capture_btn.clicked.connect(self.goto_new_capture)
        btn_layout.addWidget(new_capture_btn)

        view_captures_btn = QPushButton("View Captures")
        view_captures_btn.clicked.connect(self.goto_view_captures)
        btn_layout.addWidget(view_captures_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def goto_new_capture(self):
        # For integration, this would trigger a page switch in the main window.
        print("Navigating to new capture page")
        self.navigationRequested.emit(1)

    def goto_view_captures(self):
        print("Navigating to captures list page")
        self.navigationRequested.emit(2)
