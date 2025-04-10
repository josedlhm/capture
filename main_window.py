from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QToolBar, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon

from dashboard_widget import DashboardWidget
from capture_options_widget import CaptureOptionsWidget
from capture_widget import CaptureWidget
from captures_list_widget import CapturesListWidget
from capture_review_widget import CaptureReviewWidget
from login_widget import LoginWidget
from analysis_progress_widget import AnalysisProgressWidget  # New analysis progress page

class MainWindow(QMainWindow):
    def __init__(self, capture_service, metadata_service):
        super().__init__()
        self.setWindowTitle("Crop Camera App")
        self.resize(1200, 800)
        self.current_user = None  # Will store the logged-in username
        

        toolbar = QToolBar("Global Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        self.metadata_service = metadata_service

        # Spacer widget to push the exit button to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Create the exit action as an "X" button
        exit_action = QAction("X", self)
        exit_action.setToolTip("Exit Application")
        exit_action.triggered.connect(self.confirm_exit)
        toolbar.addAction(exit_action)

        # Style the exit button to look like your old red button, 
        # but with "X" text instead of "Exit".
        exit_button = toolbar.widgetForAction(exit_action)
        if exit_button:
            exit_button.setStyleSheet("""
                QToolButton {
                    background-color: #e74c3c;  /* red background */
                    color: white;
                    font-weight: bold;
                    font-size: 20px;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QToolButton:hover {
                    background-color: #c0392b;
                }
            """)

        # Main container and layout.
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

        # Set initial page.
        self.stacked_widget.setCurrentIndex(0)

        # Connect signals
        self.login_page.loginSuccess.connect(self.on_login_success)
        self.dashboard_page.navigationRequested.connect(self.change_page)
        self.capture_options_page.optionsSelected.connect(self.handle_capture_options)
        self.capture_page.captureCompleted.connect(self.show_capture_review)
        self.list_page.backRequested.connect(self.go_back_to_dashboard)
        # New connection: when the list page requests analysis.
        self.list_page.analysisRequested.connect(self.start_analysis)

    def confirm_exit(self):
        """Prompt for confirmation before exiting the app."""
        reply = QMessageBox.question(
            self, 
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

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

    def start_analysis(self, capture_ids):
        """
        This method is invoked when the list page emits analysisRequested.
        We create and display the AnalysisProgressWidget with the selected capture IDs.
        """
        print(f"Starting analysis for capture IDs: {capture_ids}")
        
        self.analysis_page = AnalysisProgressWidget(capture_ids, self.metadata_service)
        self.analysis_page.analysisFinished.connect(self.analysis_finished)
        self.stacked_widget.addWidget(self.analysis_page)
        self.change_page(self.stacked_widget.indexOf(self.analysis_page))

    def analysis_finished(self):
        """
        Called when the AnalysisProgressWidget signals analysisFinished.
        Remove the analysis page from the stack and navigate back to the list page.
        """
        # Remove and delete the analysis page.
        index = self.stacked_widget.indexOf(self.analysis_page)
        if index != -1:
            widget = self.stacked_widget.widget(index)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()
        self.change_page(self.stacked_widget.indexOf(self.list_page))
