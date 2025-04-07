from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt, QRect
from PySide6.QtGui import QFont, QPainter, QIcon
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QAbstractItemView, QHeaderView, QLabel, QStyleOptionButton, QStyle
)


class CheckBoxHeader(QtWidgets.QHeaderView):
    clicked = Signal(bool)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._isChecked = False
        self.setSectionsClickable(True)
        self.sectionResized.connect(self.update)
        self.sectionClicked.connect(self.handleSectionClicked)

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        if logicalIndex == 0:
            option = QStyleOptionButton()
            checkbox_size = self.style().subElementRect(
                QStyle.SE_CheckBoxIndicator, option, None
            ).size()
            x = rect.x() + (rect.width() - checkbox_size.width()) // 2
            y = rect.y() + (rect.height() - checkbox_size.height()) // 2
            option.rect = QRect(x, y, checkbox_size.width(), checkbox_size.height())
            option.state = (
                QStyle.State_Enabled
                | QStyle.State_Active
                | (QStyle.State_On if self._isChecked else QStyle.State_Off)
            )
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)

    def handleSectionClicked(self, logicalIndex):
        if logicalIndex == 0:
            self._isChecked = not self._isChecked
            self.clicked.emit(self._isChecked)
            self.viewport().update()


class CapturesListWidget(QtWidgets.QWidget):
    backRequested = Signal()

    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service

        # Window title (small, in the title bar—not a big heading)
        self.setWindowTitle("Captures")

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)
        self.setLayout(self.main_layout)

        # ---------------------------------------------------------
        # TABLE
        # ---------------------------------------------------------
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["", "ID", "File", "Time", "Status", "Crop Type", "Variety", "Location", "User"]
        )

        # Custom checkbox header for column 0
        self.checkboxHeader = CheckBoxHeader(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(self.checkboxHeader)
        self.checkboxHeader.clicked.connect(self.handle_header_checkbox_clicked)

        # Column resizing for better readability
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)

        # Alternating row colors (the actual colors can be set in style.py)
        self.table.setAlternatingRowColors(True)

        # Increase row height for better readability
        self.table.verticalHeader().setDefaultSectionSize(28)

        # Slightly larger fonts, row hover, and no hardcoded colors:
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 16px;  /* Larger for field legibility */
            }
            QTableWidget::item:hover {
                /* Row hover highlight; actual color can be styled externally */
                background-color: palette(highlight);
            }
            QHeaderView::section {
                font-weight: bold;
                border: none;
                padding: 4px;
            }
        """)

        self.main_layout.addWidget(self.table)

        # ---------------------------------------------------------
        # BOTTOM BUTTONS: Back, Analyze, Trash
        # ---------------------------------------------------------
        buttons_layout = QHBoxLayout()

        # Back button (styled externally via "role" property or style sheets)
        self.back_button = QPushButton("Back")
        self.back_button.setProperty("role", "secondary")
        buttons_layout.addWidget(self.back_button)
        self.back_button.clicked.connect(self.handle_back)

        # Stretch to push the other buttons to the right
        buttons_layout.addStretch()

        # Analyze Selected button
        self.analyze_btn = QPushButton("Analyze Selected")
        # Minimal style here; color is removed so you can do it in style.py
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
        buttons_layout.addWidget(self.analyze_btn)
        self.analyze_btn.clicked.connect(self.handle_analyze_selected)

        # Delete Selected button (trash icon)
        self.delete_btn = QPushButton()
        trash_icon = self.style().standardIcon(QStyle.SP_TrashIcon)
        self.delete_btn.setIcon(trash_icon)
        self.delete_btn.setToolTip("Delete Selected Captures")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 12px;
                border-radius: 4px;
            }
        """)
        buttons_layout.addWidget(self.delete_btn)
        self.delete_btn.clicked.connect(self.handle_delete_selected)
        self.delete_btn.setProperty("role", "secondary")

        self.main_layout.addLayout(buttons_layout)

        # Load data into the table
        self.load_captures()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_captures()

    def load_captures(self):
        captures = self.metadata_service.list_captures()
        if not captures:
            self.show_empty_state()
            return

        self.analyze_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        self.table.clearSpans()
        self.table.setRowCount(len(captures))
        self.table.setHorizontalHeaderLabels(
            ["", "ID", "File", "Time", "Status", "Crop Type", "Variety", "Location", "User"]
        )

        for row_idx, capture in enumerate(captures):
            # Optionally, rename 'ctype' to 'crop_type' for clarity:
            capture_id, filename, timestamp, status, crop_type, variety, location, user = capture

            # 0) SELECT checkbox
            select_item = QTableWidgetItem()
            select_item.setFlags(select_item.flags() | Qt.ItemIsUserCheckable)
            select_item.setCheckState(Qt.Unchecked)
            self.table.setItem(row_idx, 0, select_item)

            # 1) ID
            id_item = QTableWidgetItem(str(capture_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, id_item)

            # 2) File
            file_item = QTableWidgetItem(filename)
            file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 2, file_item)

            # 3) Time
            time_item = QTableWidgetItem(timestamp)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 3, time_item)

            # 4) Status
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 4, status_item)

            # 5) Crop Type
            type_item = QTableWidgetItem(crop_type or "")
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 5, type_item)

            # 6) Variety
            variety_item = QTableWidgetItem(variety or "")
            variety_item.setFlags(variety_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 6, variety_item)

            # 7) Location
            location_item = QTableWidgetItem(location or "")
            location_item.setFlags(location_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 7, location_item)

            # 8) User
            user_item = QTableWidgetItem(user or "")
            user_item.setFlags(user_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 8, user_item)

    def show_empty_state(self):
        """Show a friendlier empty state with a bit more guidance."""
        self.table.clearSpans()
        self.table.setRowCount(1)
        self.table.setHorizontalHeaderLabels(
            ["", "ID", "File", "Time", "Status", "Crop Type", "Variety", "Location", "User"]
        )
        placeholder = QTableWidgetItem("No captures found.\nPlease capture or import images to begin.")
        placeholder.setFlags(Qt.NoItemFlags)
        placeholder.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(0, 0, placeholder)
        self.table.setSpan(0, 0, 1, self.table.columnCount())

        self.analyze_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def handle_header_checkbox_clicked(self, checked):
        """Toggle all row checkboxes."""
        row_count = self.table.rowCount()
        # If only one row that spans all columns, it's likely the placeholder row
        if row_count == 1 and self.table.columnSpan(0) == self.table.columnCount():
            return
        for row in range(row_count):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)

    def handle_analyze_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QtWidgets.QMessageBox.information(self, "No Selection", "No captures selected.")
            return

        import os
        from config import OUTPUT_DIR
        from pipeline_trigger import trigger_pipeline  # Import the helper function

        for capture_id in selected_ids:
            capture = self.metadata_service.get_capture(capture_id)
            if not capture:
                continue
            # Capture tuple: (id, filename, timestamp, status, crop_type, variety, location, username)
            filename = capture[1]
            file_path = os.path.join(OUTPUT_DIR, filename)
            # Build a metadata dictionary from the capture record.
            metadata = {
                "crop_type": capture[4] if capture[4] else "",
                "variety": capture[5] if capture[5] else "",
                "location": capture[6] if capture[6] else "",
                "username": capture[7] if capture[7] else ""
            }
            try:
                self.metadata_service.update_status_by_id(capture_id, "analysis requested")
                result = trigger_pipeline(file_path, metadata)
                print(f"Processing result for capture {capture_id}:", result)
                self.metadata_service.update_status_by_id(capture_id, "analysis complete")
            except Exception as e:
                self.metadata_service.update_status_by_id(capture_id, "analysis failed")
                print(f"Error processing capture {capture_id}: {e}")

        QtWidgets.QMessageBox.information(
            self, "Analysis Triggered",
            f"Triggered analysis for {len(selected_ids)} capture(s)."
        )
        self.load_captures()

    def handle_delete_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QtWidgets.QMessageBox.information(self, "No Selection", "No captures selected.")
            return
        confirm = QtWidgets.QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete {len(selected_ids)} capture(s)?"
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            for capture_id in selected_ids:
                self.metadata_service.delete_capture_by_id(capture_id)
            QtWidgets.QMessageBox.information(
                self, "Deleted",
                f"Deleted {len(selected_ids)} captures."
            )
            self.load_captures()

    def get_selected_ids(self):
        """Return IDs of rows whose first-column checkboxes are checked."""
        # Check if there's only one row that's a placeholder
        if (
            self.table.rowCount() == 1
            and self.table.columnSpan(0) == self.table.columnCount()
        ):
            return []
        selected_ids = []
        for row in range(self.table.rowCount()):
            select_item = self.table.item(row, 0)
            if select_item and select_item.checkState() == Qt.Checked:
                id_item = self.table.item(row, 1)
                if id_item:
                    try:
                        capture_id = int(id_item.text())
                        selected_ids.append(capture_id)
                    except ValueError:
                        pass
        return selected_ids

    def handle_back(self):
        """Signal that the user wants to go back."""
        self.backRequested.emit()
