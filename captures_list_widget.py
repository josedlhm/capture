# captures_list_widget.py

from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton

class CapturesListWidget(QtWidgets.QWidget):
    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service

        main_layout = QVBoxLayout(self)
        
        # Increase columns to 8:
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Filename", "Timestamp", "Status",
            "Capture Type", "Variety", "Location", "Username"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        self.load_captures()

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.handle_back)
        main_layout.addWidget(self.back_button)

    def load_captures(self):
        # Now we get everything including username from list_captures
        captures = self.metadata_service.list_captures()
        self.table.setRowCount(len(captures))

        for row_idx, capture in enumerate(captures):
            # capture is a tuple: 
            # (id, filename, timestamp, status, capture_type, variety, location, username)
            (
                capture_id, filename, timestamp, status,
                capture_type, variety, location, username
            ) = capture

            self.table.setItem(row_idx, 0, QTableWidgetItem(str(capture_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(filename))
            self.table.setItem(row_idx, 2, QTableWidgetItem(timestamp))
            self.table.setItem(row_idx, 3, QTableWidgetItem(status))
            self.table.setItem(row_idx, 4, QTableWidgetItem(capture_type or ""))
            self.table.setItem(row_idx, 5, QTableWidgetItem(variety or ""))
            self.table.setItem(row_idx, 6, QTableWidgetItem(location or ""))
            self.table.setItem(row_idx, 7, QTableWidgetItem(username or ""))
        
        self.table.resizeColumnsToContents()

    def handle_back(self):
        print("Back button pressed. Use the side navigation to switch pages.")
