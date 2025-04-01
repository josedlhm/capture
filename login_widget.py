# login_widget.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Signal, Qt

class LoginWidget(QWidget):
    # This signal will emit the username (and possibly password)
    loginSuccess = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QLabel, QLineEdit {
                font-size: 18px;
                color: #e0e0e0;
            }
            QPushButton {
                font-size: 20px;
                padding: 10px 20px;
                background-color: #444444;
                color: white;
                border: 2px solid #666;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QWidget {
                background-color: #2c2c2c;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.label_title = QLabel("Please Log In")
        self.label_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_title)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        layout.addWidget(self.username_edit)

        # If you wanted a password field:
        # self.password_edit = QLineEdit()
        # self.password_edit.setPlaceholderText("Password")
        # self.password_edit.setEchoMode(QLineEdit.Password)
        # layout.addWidget(self.password_edit)

        self.button_login = QPushButton("Log In")
        self.button_login.clicked.connect(self.handle_login)
        layout.addWidget(self.button_login)

    def handle_login(self):
        username = self.username_edit.text().strip()
        if not username:
            return  # or show a message box "Username cannot be empty"

        # In a real system, you'd verify the username/password here
        # For a minimal example, we accept anything non-empty.
        self.loginSuccess.emit(username)
