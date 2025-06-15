
import sys
import pandas as pd
import logging
from PyQt5.QtWidgets import (
    QApplication
)
from ui.main_window import MainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

def load_stylesheet():
    """
    Load the application stylesheet.
    
    Returns:
        str: Stylesheet content
    """
    # Define a modern stylesheet
    stylesheet = """
    QMainWindow {
        background-color: #f5f5f5;
    }
    
    QTabWidget::pane {
        border: 1px solid #ddd;
        background-color: white;
        border-radius: 3px;
    }
    
    QTabBar::tab {
        background-color: #f0f0f0;
        color: #555;
        padding: 8px 12px;
        margin-right: 2px;
        border: 1px solid #ddd;
        border-bottom: none;
        border-top-left-radius: 3px;
        border-top-right-radius: 3px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        border-bottom-color: white;
        color: #333;
    }
    
    QGroupBox {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 3px;
        margin-top: 15px;
        padding-top: 15px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 5px;
        background-color: white;
        color: #555;
    }
    
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        border: 1px solid #ddd;
        border-radius: 3px;
        padding: 4px;
        background-color: white;
        selection-background-color: #007bff;
    }
    
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border: 1px solid #007bff;
    }
    
    QPushButton {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 3px;
        padding: 6px 12px;
    }
    
    QPushButton:hover {
        background-color: #0069d9;
    }
    
    QPushButton:pressed {
        background-color: #0062cc;
    }
    
    QPushButton:disabled {
        background-color: #ccc;
    }
    
    QTableWidget {
        gridline-color: #ddd;
        background-color: white;
        selection-background-color: #e9ecef;
        selection-color: #212529;
    }
    
    QHeaderView::section {
        background-color: #f8f9fa;
        color: #495057;
        padding: 5px;
        border: 1px solid #ddd;
    }
    
    QScrollBar:vertical {
        border: none;
        background: #f0f0f0;
        width: 10px;
        margin: 0px;
    }
    
    QScrollBar::handle:vertical {
        background: #c0c0c0;
        min-height: 20px;
        border-radius: 5px;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
    }
    
    QListWidget {
        border: 1px solid #ddd;
        background-color: white;
    }
    
    QRadioButton {
        spacing: 8px;
    }
    
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
    }
    
    QToolBar {
        background-color: #f8f9fa;
        border-bottom: 1px solid #ddd;
        spacing: 5px;
    }
    
    QStatusBar {
        background-color: #f8f9fa;
        color: #6c757d;
    }
    """
    
    return stylesheet

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('debug.log', mode='w')
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting...")

    app = QApplication(sys.argv)

    app.setApplicationName("VINCENZO 2025")
    app.setOrganizationName("IPSOS")

    # Apply StyleSheet
    app.setStyleSheet(load_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
