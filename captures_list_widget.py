# captures_list_widget.py
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Qt, QRect, QThread, QObject, Slot
from PySide6.QtGui import QFont, QPainter, QIcon
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QAbstractItemView, QHeaderView, QLabel, QStyleOptionButton, QStyle, QMessageBox
)
import os
from config import OUTPUT_DIR
from pipeline_trigger import trigger_pipeline  # No longer used in this widget

class CheckBoxHeader(QtWidgets.QHeaderView):
    clicked = Signal(bool)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._isChecked = False
        self.setSectionsClickable(True)
        self.sectionResized.connect(self.update)
        self.sectionClicked.connect(self.handleSectionClicked)

    def paintSection(self, painter, rect, logicalIndex):
        if logicalIndex == 0:
            option = QStyleOptionButton()
            checkbox_size = self.style().subElementRect(QStyle.SE_CheckBoxIndicator, option, None).size()
            x = rect.x() + (rect.width() - checkbox_size.width()) // 2
            y = rect.y() + (rect.height() - checkbox_size.height()) // 2
            option.rect = QRect(x, y, checkbox_size.width(), checkbox_size.height())
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self._isChecked:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            self.style().drawControl(QStyle.CE_CheckBox, option, painter)
        else:
            super().paintSection(painter, rect, logicalIndex)

    def handleSectionClicked(self, logicalIndex):
        if logicalIndex == 0:
            self._isChecked = not self._isChecked
            self.clicked.emit(self._isChecked)
            self.viewport().update()


class CapturesListWidget(QtWidgets.QWidget):
    backRequested = Signal()
    # New signal that emits a list of selected capture IDs.
    analysisRequested = Signal(list)

    def __init__(self, capture_service, metadata_service, parent=None):
        super().__init__(parent)
        self.capture_service = capture_service
        self.metadata_service = metadata_service
        # (The analysis_threads list from before is no longer needed here.)
        self.setWindowTitle("Captures")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)
        self.setLayout(self.main_layout)

        # Setup table with checkboxes.
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ["", "ID", "File", "Time", "Status", "Crop Type", "Variety", "Location", "User"]
        )

        self.checkboxHeader = CheckBoxHeader(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(self.checkboxHeader)
        self.checkboxHeader.clicked.connect(self.handle_header_checkbox_clicked)

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

        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 16px;
            }
            QTableWidget::item:hover {
                background-color: palette(highlight);
            }
            QHeaderView::section {
                font-weight: bold;
                border: none;
                padding: 4px;
            }
        """)

        self.main_layout.addWidget(self.table)

        # Bottom buttons: Back, Analyze, Delete.
        buttons_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.setProperty("role", "secondary")
        buttons_layout.addWidget(self.back_button)
        self.back_button.clicked.connect(self.handle_back)

        buttons_layout.addStretch()

        self.analyze_btn = QPushButton("Analyze Selected")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
        buttons_layout.addWidget(self.analyze_btn)
        self.analyze_btn.clicked.connect(self.handle_analyze_selected)

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
        self.table.verticalHeader().setVisible(False)
        self.table.setFocusPolicy(Qt.NoFocus)

        for row_idx, capture in enumerate(captures):
            # Capture tuple: (id, filename, timestamp, status, crop_type, variety, location, user)
            capture_id, filename, timestamp, status, crop_type, variety, location, user = capture

            # Column 0: Checkbox.
            select_item = QTableWidgetItem()
            select_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            select_item.setCheckState(Qt.Unchecked)
            select_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, select_item)

            # Column 1: ID.
            id_item = QTableWidgetItem(str(capture_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, id_item)

            # Column 2: File name.
            file_item = QTableWidgetItem(filename)
            file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 2, file_item)

            # Column 3: Time.
            time_item = QTableWidgetItem(timestamp)
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 3, time_item)

            # Column 4: Status.
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 4, status_item)

            # Column 5: Crop Type.
            type_item = QTableWidgetItem(crop_type or "")
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 5, type_item)

            # Column 6: Variety.
            variety_item = QTableWidgetItem(variety or "")
            variety_item.setFlags(variety_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 6, variety_item)

            # Column 7: Location.
            location_item = QTableWidgetItem(location or "")
            location_item.setFlags(location_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 7, location_item)

            # Column 8: User.
            user_item = QTableWidgetItem(user or "")
            user_item.setFlags(user_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row_idx, 8, user_item)

    def show_empty_state(self):
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
        row_count = self.table.rowCount()
        if row_count == 1 and self.table.columnSpan(0, 0) == self.table.columnCount():
            return
        for row in range(row_count):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)

    def reset_checkboxes(self):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(Qt.Unchecked)
        self.checkboxHeader._isChecked = False
        self.checkboxHeader.viewport().update()

    def get_selected_ids(self):
        if self.table.rowCount() == 1 and self.table.columnSpan(0, 0) == self.table.columnCount():
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

    # Modified handle_analyze_selected: Instead of processing analysis here, emit a signal.
    def handle_analyze_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.information(self, "No Selection", "No captures selected. Please select at least one capture.")
            return

        # Emit the list of selected capture IDs so the main window can navigate to the analysis progress page.
        self.analysisRequested.emit(selected_ids)

    def handle_delete_selected(self):
        selected_ids = self.get_selected_ids()
        if not selected_ids:
            QMessageBox.information(self, "No Selection", "No captures selected. Please select at least one capture to delete.")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete {len(selected_ids)} capture(s)?")
        if confirm == QMessageBox.Yes:
            for capture_id in selected_ids:
                self.metadata_service.delete_capture_by_id(capture_id)
            QMessageBox.information(self, "Deleted", f"Deleted {len(selected_ids)} captures.")
            self.load_captures()
        self.reset_checkboxes()

    def handle_back(self):
        self.backRequested.emit()
