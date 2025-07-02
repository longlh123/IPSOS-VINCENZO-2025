import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QAction, QGroupBox, QGridLayout, QComboBox, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.Qt import Qt
from ui.widgets.NPSBarChartWidget import NPSBarChartWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class ReportTab(QWidget):

    def __init__(self, data=None, config=None):
        super().__init__()

        self.data = data.copy() if data is not None else pd.DataFrame()
        self.config = config

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
            
            # Create a widget for the scroll area
        scroll_content = QWidget()
        
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(15)

        self.placeholder_lable = QLabel("Vui lòng mở file dữ liệu để xem báo cáo")
        self.placeholder_lable.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.placeholder_lable)
    
        self.scroll_layout.addStretch()
            
        # Set the scroll area widget
        scroll_area.setWidget(scroll_content)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
    
    def clear_layout(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def update_data(self, df: pd.DataFrame, config=None):
        
        self.clear_layout()

        self.data = df.copy()
        self.config = config
        
        for key, dataset in self.config.items():
            if "dataset" in key:
                chart_group = self.create_chart_group(dataset)

                self.scroll_layout.addWidget(chart_group)

    def create_chart_group(self, dataset):
        self.chart_group = QGroupBox(dataset.get('chart_name'))

        self.load_data(dataset)

        self.chart_group_layout = QVBoxLayout()
        self.chart_group.setLayout(self.chart_group_layout)
        
        return self.chart_group
    
    def load_data(self, dataset):
        df = self.data[dataset.get('used-cols', [])].copy()

        df = df.rename(columns=dataset.get('rename-columns', {}))
        
        df_nps_long = pd.wide_to_long(
            df,
            stubnames=list(dataset.get('stubnames', {}).keys()),
            i = dataset.get('i-cols', []),
            j = dataset.get('j-col', ''),
            sep='###',
            suffix='\\d+'
        )

        df_nps_long = df_nps_long.dropna(subset=["Q1", "Q2_NPS"])

        chart_data = df_nps_long.groupby(["Q1", "Wave"]).apply(self.calculate_nps_components).reset_index()

        # Thêm biểu đồ mới
        self.chart_widget = NPSBarChartWidget(chart_data)
        
        self.chart_group_layout.addWidget(self.chart_widget)

    def calculate_nps_components(self, group):
        total = len(group)

        promoters = ((group["Q2_NPS"] == 9) | (group["Q2_NPS"] == 10)).sum()
        detractors = ((group["Q2_NPS"] >= 0) & (group["Q2_NPS"] <= 6)).sum()
        passives = ((group["Q2_NPS"] >= 7) & (group["Q2_NPS"] <= 8)).sum()

        return pd.Series({
            "Promoter" : round(promoters / total * 100, 2),
            "Passive" : round(passives / total * 100, 2),
            "Detractor" : round(detractors / total * 100, 2),
            "NPS" : round((promoters - detractors) / total * 100, 2)
        })