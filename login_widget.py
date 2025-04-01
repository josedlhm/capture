from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

class LoginWidget(QWidget):
    loginSuccess = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QWidget {

                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #2d3a35;
            }
            QLineEdit {
                font-size: 16px;
                padding: 10px;
                border: 1px solid #b2d8cc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #333;
            }
            QLineEdit:focus {
                border: 1px solid #00B894;
            }
            QPushButton {
                font-size: 16px;
                font-weight: 600;
                padding: 10px;
                background-color: #00B894;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #00cc9d;
            }
            QPushButton:pressed {
                background-color: #009c77;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Container "card"
        self.container = QFrame()
        self.container.setFixedWidth(320)
        self.container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 16px;
                padding: 30px;
                border: 1px solid #ececec;
            }
        """)
        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Title
        self.label_title = QLabel("🌱 Macanudo", self.container)
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setStyleSheet("""
            background: transparent; 
            border: none; 
            font-size: 22px; 
            font-weight: 600; 
            letter-spacing: 0.5px;
            color: #2d3a35;
        """)
        self.label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_title)

        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        layout.addWidget(self.username_edit)

        # Login button
        self.button_login = QPushButton("Log In")
        self.button_login.clicked.connect(self.handle_login)
        layout.addWidget(self.button_login)

        main_layout.addWidget(self.container)

    def handle_login(self):
        username = self.username_edit.text().strip()
        if not username:
            return
        self.loginSuccess.emit(username)
