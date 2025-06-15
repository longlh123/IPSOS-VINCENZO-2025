import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QAction, QGroupBox, QGridLayout, QComboBox, QHBoxLayout, QTabWidget
)
from PyQt5.Qt import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from ui.tabs.NPSTab import NPSTab
from ui.widgets.multi_select import MultiSelectWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up logging
        self.logger = logging.getLogger(__name__)

        self.df = pd.DataFrame()

        self.setWindowTitle("VINCENZO 2025")
        self.resize(1100, 800)

        self.filters = {}
        
        #Lưu trữ filter combobox
        self.multiselectitems = {}

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.filter_group = self.create_filter_group()

        main_layout.addWidget(self.filter_group, alignment=Qt.AlignTop)

        # Create tab widget
        self.tab_widget = QTabWidget()

        self.nps_tab = NPSTab(self.df)

        self.tab_widget.addTab(self.nps_tab, "NPS Report")

        self.setCentralWidget(central_widget)

        main_layout.addWidget(self.tab_widget)

        self.create_menu_bar()

        self.statusBar().showMessage("Ready")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+P")
        open_action.triggered.connect(self.load_file)
        file_menu.addAction(open_action)
    
    def create_filter_group(self):
        groupbox = QGroupBox("Filter")
        
        form_layout = QGridLayout(groupbox)
        form_layout.setColumnStretch(1, 1)

        self.multiselectitems = {}
        
        row = 0

        for key in self.filters:
            form_layout.addWidget(QLabel(f"{key}:"), row, 0)

            multiselectitem = MultiSelectWidget(self.filters[key])

            multiselectitem.selectionChanged.connect(
                lambda items: self.handle_filter_changed(key, items)
            )
                
            form_layout.addWidget(multiselectitem, row, 1)
            self.multiselectitems[key] = multiselectitem

            row += 1

        return groupbox

    def handle_filter_changed(self, column_name: str, value: str):

        filtered_df = self.df.copy()

        for key, values in self.filters.items():
            multiselectitem = self.multiselectitems[key]
            selected_items = multiselectitem.get_selected_items()

            if len(selected_items) > 0:
                filtered_df = filtered_df.loc[filtered_df[key].isin(selected_items)]

        # Cập nhật dữ liệu cho tab NPS
        self.nps_tab.update_data(filtered_df)


        print(f"{column_name} changed to {value}")

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file CSV", "", "CSV Files (*.csv)")

        if not file_path:
            return

        config_path = file_path.replace(".csv", "_config.json")  

        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Không tìm thấy file cấu hình: {config_path}")
            
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            self.filters = config["filters"]
            usecols = config["dataset"]["usecols"]
            self.df = pd.read_csv(file_path, encoding='utf-8', usecols=usecols)

            # needed_cols = ["Respondent.ID", "Wave", "Region", "Province", "Segment" ,"_Q6e_Main bank","_Main bank_Comp 1","_Main bank_Comp 2","_Q9_NPS TCB","_Q9_NPS Comp 1","_Q9_NPS Comp 2"]

            self.df = pd.read_csv(file_path, encoding='utf-8', usecols=usecols)
            
            self.filters = config["filters"]
            
            self.filter_group = self.create_filter_group()

            self.set_filters(self.df)

            self.update_from_model()
        except Exception as e:
            self.logger.error(f"Không tìm thấy file cấu hình: {config_path}")
            QMessageBox.critical(
                self,
                "Error",
                f"Lỗi: {e}",
            )
    
    def set_filters(self, df):
        for column_name in self.filters.keys():
            self.filters[column_name] = df[column_name].dropna().unique().tolist()

    def update_from_model(self):
        try:
            for key, values in self.filters.items():
                multiselectitem = self.multiselectitems[key]
                multiselectitem.set_items(values)
            
            # Cập nhật dữ liệu cho tab NPS
            self.nps_tab.update_data(self.df)
        except Exception as e:
            self.logger.error(f"Error updating model: {e}")



