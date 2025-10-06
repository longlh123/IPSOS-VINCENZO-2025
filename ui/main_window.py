import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import re

import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QAction, QGroupBox, QGridLayout, QComboBox, QHBoxLayout, QTabWidget, QSizePolicy
)
from PyQt5.Qt import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from ui.tabs.NPSReportTab import NPSReportTab
from ui.tabs.ReportTab import ReportTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up logging
        self.logger = logging.getLogger(__name__)

        self.df = pd.DataFrame()
        self.config = {}

        self.setWindowTitle("VINCENZO 2025")
        self.resize(1200, 1280)

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.create_menu_bar()

        # Create tab widget
        self.tab_widget = QTabWidget()

        self.setCentralWidget(central_widget)

        main_layout.addWidget(self.tab_widget)

        self.clear_all_tabs()
        self.show_placeholder_tab()

        self.statusBar().showMessage("Ready")

    def clear_all_tabs(self):
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(self.tab_widget.count() - 1)

    def show_placeholder_tab(self, message="Vui lòng mở file dữ liệu để xem báo cáo"):
        placeholder_tab = QWidget()
        layout = QVBoxLayout(placeholder_tab)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.tab_widget.addTab(placeholder_tab, "Report")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+P")
        open_action.triggered.connect(self.load_file)
        file_menu.addAction(open_action)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file CSV", "", "CSV Files (*.csv)")

        if not file_path:
            return

        config_path = file_path.replace(".csv", "_config.json")  

        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Không tìm thấy file cấu hình: {config_path}")
            
            self.clear_all_tabs()

            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

            self.df = pd.read_csv(file_path, encoding='utf-8')
            
            for key, dataset in self.config.items():
                report_tab = None

                report_tab = NPSReportTab(data=self.df, dataset=dataset)
                
                if report_tab is not None:
                    self.tab_widget.addTab(report_tab, dataset.get('chart', {}).get('title', ''))
        except Exception as e:
            self.logger.error(f"Không tìm thấy file cấu hình: {config_path}")
            QMessageBox.critical(
                self,
                "Error",
                f"Lỗi: {e}",
            )
    

