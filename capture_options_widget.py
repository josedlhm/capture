# capture_options_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFormLayout, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Signal, Qt

class CaptureOptionsWidget(QWidget):
    # Signal to emit when the options are confirmed.
    # The emitted dict contains the selected options.
    optionsSelected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)  # Generous margins for spacing
        main_layout.setSpacing(30)

        # Title
        title = QLabel("Capture Options")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Form layout for capture details
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(30)
        form_layout.setVerticalSpacing(20)

        # 1. Crop Type: Grapes or Blueberries
        self.crop_type_combo = QComboBox()
        self.crop_type_combo.addItems(["Grapes", "Blueberries"])
        self.crop_type_combo.currentIndexChanged.connect(self.update_variety_options)
        form_layout.addRow(self._styled_label("Crop Type:"), self.crop_type_combo)
        
        # 2. Variety (drop down, dependent on crop type)
        self.variety_combo = QComboBox()
        form_layout.addRow(self._styled_label("Variety:"), self.variety_combo)
        # Initialize variety options for the default crop type selection
        self.update_variety_options()
        
        # 3. Location remains a text field
        self.location_line = QLineEdit()
        self.location_line.setPlaceholderText("Enter location")
        form_layout.addRow(self._styled_label("Location:"), self.location_line)

        main_layout.addLayout(form_layout)
        
        # Spacer to push the button down if the screen is tall
        main_layout.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Proceed button
        self.proceed_button = QPushButton("Proceed to Capture")
        self.proceed_button.clicked.connect(self.handle_proceed)
        self.proceed_button.setMinimumHeight(60)  # Larger button height
        main_layout.addWidget(self.proceed_button)
    
    def _styled_label(self, text):
        """Helper to create form labels with consistent styling."""
        label = QLabel(text)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return label

    def handle_proceed(self):
        # Gather the selected options.
        options = {
            "crop_type": self.crop_type_combo.currentText(),
            "variety": self.variety_combo.currentText(),
            "location": self.location_line.text()
        }
        print("Selected Options:", options)
        # Emit the signal so the main window can navigate.
        self.optionsSelected.emit(options)

    def update_variety_options(self):
        crop_type = self.crop_type_combo.currentText()
        self.variety_combo.clear()
        if crop_type == "Grapes":
            self.variety_combo.addItems(["Real", "Plastic"])
        elif crop_type == "Blueberries":
            self.variety_combo.addItem("Real")
