# capture_options_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFormLayout
)
from PySide6.QtCore import Signal, Qt

class CaptureOptionsWidget(QWidget):
    # Signal to emit when the options are confirmed.
    # The emitted dict contains the selected options.
    optionsSelected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget { background-color: #2c2c2c; }
            QLabel { color: white; font-size: 18px; }
            QPushButton { font-size: 20px; padding: 10px; background-color: #444444; color: white; border: 2px solid #666; border-radius: 5px; }
            QPushButton:hover { background-color: #555555; }
            QLineEdit, QComboBox { font-size: 16px; padding: 5px; background-color: #3b3b3b; color: white; }
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title/Instruction
        title = QLabel("Capture Options")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Form layout to organize the fields.
        form_layout = QFormLayout()
        
        # 1. Capture Type: Grapes or Blueberries.
        self.capture_type_combo = QComboBox()
        self.capture_type_combo.addItems(["Grapes", "Blueberries"])
        form_layout.addRow("Capture Type:", self.capture_type_combo)
        
        # 2. Variety: A text field where the user can input or select a variety.
        self.variety_line = QLineEdit()
        self.variety_line.setPlaceholderText("Enter variety")
        form_layout.addRow("Variety:", self.variety_line)
        
        # 3. Location: A text field to specify where the capture is taken.
        self.location_line = QLineEdit()
        self.location_line.setPlaceholderText("Enter location")
        form_layout.addRow("Location:", self.location_line)
        
        layout.addLayout(form_layout)
        
        # Button to confirm options and proceed.
        self.proceed_button = QPushButton("Proceed to Capture")
        self.proceed_button.clicked.connect(self.handle_proceed)
        layout.addWidget(self.proceed_button)
    
    def handle_proceed(self):
        # Gather the selected options.
        options = {
            "capture_type": self.capture_type_combo.currentText(),
            "variety": self.variety_line.text(),
            "location": self.location_line.text()
        }
        print("Selected Options:", options)
        # Emit the signal so the main window can navigate.
        self.optionsSelected.emit(options)
