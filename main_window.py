from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PySide6.QtCore import Qt

from dashboard_widget import DashboardWidget  # Dashboard page.
from capture_options_widget import CaptureOptionsWidget  # New Capture Options page.
from capture_widget import CaptureWidget
from captures_list_widget import CapturesListWidget
from capture_review_widget import CaptureReviewWidget

class MainWindow(QMainWindow):
    def __init__(self, capture_service, metadata_service):
        super().__init__()
        self.setWindowTitle("Crop Camera App")
        self.resize(1200, 800)

        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)

        # Side navigation panel.
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_widget.setFixedWidth(200)
       
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.clicked.connect(lambda: self.change_page(0))
        nav_layout.addWidget(self.btn_dashboard)

        self.btn_new_capture = QPushButton("New Capture")
        self.btn_new_capture.clicked.connect(lambda: self.change_page(1))
        nav_layout.addWidget(self.btn_new_capture)
        
        self.btn_list = QPushButton("Captures List")
        self.btn_list.clicked.connect(lambda: self.change_page(3))
        nav_layout.addWidget(self.btn_list)

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close)
        nav_layout.addWidget(self.btn_exit)
        
        nav_layout.addStretch()
        main_layout.addWidget(nav_widget)

        # QStackedWidget for the pages.
        self.stacked_widget = QStackedWidget()
        self.dashboard_page = DashboardWidget(capture_service, metadata_service)
        self.capture_options_page = CaptureOptionsWidget()
        self.capture_page = CaptureWidget(capture_service, metadata_service)
        self.list_page = CapturesListWidget(capture_service, metadata_service)
        
        self.stacked_widget.addWidget(self.dashboard_page)         # Index 0.
        self.stacked_widget.addWidget(self.capture_options_page)     # Index 1.
        self.stacked_widget.addWidget(self.capture_page)             # Index 2.
        self.stacked_widget.addWidget(self.list_page)                # Index 3.
        main_layout.addWidget(self.stacked_widget)

        # Connect signals:
        self.dashboard_page.navigationRequested.connect(self.change_page)
        self.capture_options_page.optionsSelected.connect(self.handle_capture_options)
        # Here we connect the captureCompleted signal from capture_page.
        self.capture_page.captureCompleted.connect(self.show_capture_review)

        self.stacked_widget.setCurrentIndex(0)

    def change_page(self, index):
        print(f"Changing to page {index}")
        self.stacked_widget.setCurrentIndex(index)
    
    def handle_capture_options(self, options):
        print("Received capture options:", options)
        # Navigate to the actual capture screen.
        self.change_page(2)
    
    def show_capture_review(self, capture_file, metadata):
        print("Showing capture review for:", capture_file)
        # Create the review widget.
        review_widget = CaptureReviewWidget(capture_file, metadata)
        review_widget.reviewCompleted.connect(self.handle_review_completed)
        # Add review widget to the stacked widget.
        self.stacked_widget.addWidget(review_widget)
        # Switch to the review widget.
        self.change_page(self.stacked_widget.indexOf(review_widget))
    
    def handle_review_completed(self, action):
        print(f"Review action: {action}")
        if action == "delete":
            # Delete file and update metadata if necessary.
            self.change_page(0)  # Return to Dashboard.
        elif action == "new_capture":
            self.change_page(1)  # Navigate to Capture Options for a new capture.
        elif action == "dashboard":
            self.change_page(0)  # Navigate to Dashboard.
