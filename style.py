# style.py

def load_stylesheet() -> str:
    """
    Returns the global stylesheet with tablet-friendly dimensions.
    """
    return """
        /* GLOBALS */
        QWidget {
            font-family: 'Segoe UI', sans-serif;
            color: #2d3a35;
            font-size: 18px;  /* increased base font size for tablet readability */
        }

        /* HEADINGS */
        QLabel#Header, QLabel[role="header"] {
            font-size: 28px;  /* larger heading font */
            font-weight: 600;
            letter-spacing: 0.5px;
            color: #2d3a35;
            margin-bottom: 20px;  /* extra spacing for clarity */
        }

        /* BUTTONS */
        QPushButton {
            font-size: 20px;  /* larger text for easier tap targets */
            font-weight: 600;
            color: #ffffff;
            background-color: #00B894;
            border: none;
            border-radius: 10px;  /* slightly larger rounding */
            padding: 14px 28px;   /* increased padding for comfortable tapping */
        }
        QPushButton:hover { 
            background-color: #00cc9d; 
        }
        QPushButton:pressed { 
            background-color: #009c77; 
        }

        /* INPUT FIELDS */
        QLineEdit, QComboBox, QTableWidget, QTableView {
            font-size: 18px;
            border: 1px solid #b2d8cc;
            border-radius: 8px;
            padding: 8px 12px;  /* increased padding for touch */
            color: #2d3a35;
            background: #ffffff;
        }
        QLineEdit:focus, QComboBox:focus, QTableWidget:focus, QTableView:focus {
            border: 1px solid #00B894;
        }

        /* TABLE HEADERS */
        QHeaderView::section {
            font-weight: 600;
            background-color: #f0f0f0;
            border: none;
            padding: 10px;
        }

        /* CARD STYLE */
        QFrame[role="card"] {
            background-color: #ffffff;
            border-radius: 14px;
            border: 1px solid #ececec;
            padding: 24px;
        }

        /* SECONDARY BUTTONS */
        QPushButton[role="secondary"] {
            background-color: #7f8c8d;
            color: #ffffff;
        }
        QPushButton[role="secondary"]:hover {
            background-color: #95a5a6;
        }
        QPushButton[role="secondary"]:pressed {
            background-color: #6c7a7d;
        }

        /* TOOLBAR */
        QToolBar {
            background-color: #00B894;  /* matching primary button color for consistency */
            padding: 8px;
            spacing: 10px;
            border: none;
        }
        QToolBar QToolButton {
            color: #ffffff;
            font-size: 20px;
            padding: 4px 12px;
            background: transparent;
            border: none;
        }
    """
