# captures_list_widget.py
from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton

class CapturesListWidget(QtWidgets.QWidget):
    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service

        # Apply a consistent dark style.
        self.setStyleSheet("""
            QWidget { background-color: #2c2c2c; }
            QTableWidget { background-color: #3b3b3b; color: white; gridline-color: #555; }
            QHeaderView::section { background-color: #444444; color: white; }
            QPushButton { font-size: 16px; padding: 8px; background-color: #444444; color: white; border: 2px solid #666; border-radius: 5px; }
            QPushButton:hover { background-color: #555555; }
        """)

        main_layout = QVBoxLayout(self)
        
        # Table for displaying captures.
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Filename", "Timestamp", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        self.load_captures()

        # Optional Back button (navigation is also available via the side menu).
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.handle_back)
        main_layout.addWidget(self.back_button)

    def load_captures(self):
        captures = self.metadata_service.list_captures()  # List of tuples: (id, filename, timestamp, status)
        self.table.setRowCount(len(captures))
        for row_idx, capture in enumerate(captures):
            capture_id, filename, timestamp, status = capture
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(capture_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(filename))
            self.table.setItem(row_idx, 2, QTableWidgetItem(timestamp))
            self.table.setItem(row_idx, 3, QTableWidgetItem(status))
        self.table.resizeColumnsToContents()

    def handle_back(self):
        # For this example, we simply print a message.
        # In a full implementation, you could emit a signal to the main window to switch pages.
        print("Back button pressed. Use the side navigation to switch pages.")
