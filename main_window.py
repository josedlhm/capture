# main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt

from dashboard_widget import DashboardWidget
from capture_options_widget import CaptureOptionsWidget
from capture_widget import CaptureWidget
from captures_list_widget import CapturesListWidget
from capture_review_widget import CaptureReviewWidget
from login_widget import LoginWidget

class MainWindow(QMainWindow):
    def __init__(self, capture_service, metadata_service):
        super().__init__()
        self.setWindowTitle("Crop Camera App")
        self.resize(1200, 800)

        self.current_user = None  # Will store the logged-in username

        container = QWidget()
        self.setCentralWidget(container)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.login_page = LoginWidget()
        self.dashboard_page = DashboardWidget(capture_service, metadata_service)
        self.capture_options_page = CaptureOptionsWidget()
        self.capture_page = CaptureWidget(capture_service, metadata_service)
        self.list_page = CapturesListWidget(capture_service, metadata_service)

        self.stacked_widget.addWidget(self.login_page)            # Index 0
        self.stacked_widget.addWidget(self.dashboard_page)        # Index 1
        self.stacked_widget.addWidget(self.capture_options_page)  # Index 2
        self.stacked_widget.addWidget(self.capture_page)          # Index 3
        self.stacked_widget.addWidget(self.list_page)             # Index 4

        self.stacked_widget.setCurrentIndex(0)

        self.login_page.loginSuccess.connect(self.on_login_success)
        self.dashboard_page.navigationRequested.connect(self.change_page)
        self.capture_options_page.optionsSelected.connect(self.handle_capture_options)
        self.capture_page.captureCompleted.connect(self.show_capture_review)

        self.list_page.backRequested.connect(self.go_back_to_dashboard)
    
    def go_back_to_dashboard(self):
        self.change_page(1)

    def on_login_success(self, username):
        self.current_user = username
        print("Logged in as:", username)
        self.change_page(1)

    def change_page(self, index):
        if self.current_user is None and index != 0:
            print("Must be logged in to view other pages!")
            self.stacked_widget.setCurrentIndex(0)
            return

        print(f"Changing to page {index}")
        self.stacked_widget.setCurrentIndex(index)

    def handle_capture_options(self, options):
        print("Received capture options:", options)
        options["username"] = self.current_user
        self.current_capture_options = options
        self.capture_page.capture_options = options  # Pass options to the capture widget
        self.change_page(3)

    def show_capture_review(self, capture_file, metadata):
        print("Showing capture review for:", capture_file)
        review_widget = CaptureReviewWidget(capture_file, metadata)
        review_widget.reviewCompleted.connect(self.handle_review_completed)
        self.stacked_widget.addWidget(review_widget)
        self.change_page(self.stacked_widget.indexOf(review_widget))

    def handle_review_completed(self, action):
        print(f"Review action: {action}")
        if action == "delete":
            self.change_page(1)
        elif action == "new_capture":
            self.change_page(2)
        elif action == "dashboard":
            self.change_page(1)
