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

class NPSTab(QWidget):

    def __init__(self, data):
        super().__init__()

        self.data = data.copy()
        
        if not self.data.empty:
            # Main layout
            main_layout = QVBoxLayout(self)
            
            # Create a scroll area
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QFrame.NoFrame)
            
            # Create a widget for the scroll area
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(15)

            nps_chart_group = self.create_nps_chart_group()

            scroll_layout.addWidget(nps_chart_group)

            scroll_layout.addStretch()
            
            # Set the scroll area widget
            scroll_area.setWidget(scroll_content)
            
            # Add scroll area to main layout
            main_layout.addWidget(scroll_area)

    def create_nps_chart_group(self):
        self.nps_chart_group = QGroupBox("NPS")

        self.nps_chart_group_layout = QVBoxLayout()
        self.nps_chart_group.setLayout(self.nps_chart_group_layout)
        
        return self.nps_chart_group
    
    def update_data(self, df: pd.DataFrame):
        self.data = df.copy()
        self.load_data()

    def load_data(self):
        needed_cols = ["Respondent.ID", "Wave", "Region", "Province" ,"_Q6e_Main bank","_Main bank_Comp 1","_Main bank_Comp 2","_Q9_NPS TCB","_Q9_NPS Comp 1","_Q9_NPS Comp 2"]

        df_nps = self.data[needed_cols].copy()

        df_nps["_Q6e_Main bank"] = "Techcombank"
        
        df_nps.rename(columns={
            "_Q6e_Main bank" : "Main_Bank_1",
            "_Main bank_Comp 1" : "Main_Bank_2",
            "_Main bank_Comp 2" : "Main_Bank_3",
            "_Q9_NPS TCB" : "NPS_1",
            "_Q9_NPS Comp 1" : "NPS_2",
            "_Q9_NPS Comp 2" : "NPS_3"
        }, inplace=True)

        df_nps.set_index(["Respondent.ID"], inplace=True)

        df_nps_long = pd.wide_to_long(
            df_nps.reset_index(),
            stubnames=["Main_Bank", "NPS"],
            i = ["Respondent.ID", "Wave", "Region", "Province"],
            j = 'Bank_Order',
            sep='_',
            suffix='\\d+'
        ).reset_index()

        df_nps_long = df_nps_long.dropna(subset=["Main_Bank", "NPS"])

        chart_data = df_nps_long.groupby(["Main_Bank", "Wave"]).apply(self.calculate_nps_components).reset_index()

        # Xóa biểu đồ cũ nếu có
        while self.nps_chart_group_layout.count():
            item = self.nps_chart_group_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        # Thêm biểu đồ mới
        self.chart_widget = NPSBarChartWidget(chart_data)
        self.nps_chart_group_layout.addWidget(self.chart_widget)

    def calculate_nps_components(self, group):
        total = len(group)

        promoters = ((group["NPS"] == 9) | (group["NPS"] == 10)).sum()
        detractors = ((group["NPS"] >= 0) & (group["NPS"] <= 6)).sum()
        passives = ((group["NPS"] >= 7) & (group["NPS"] <= 8)).sum()

        return pd.Series({
            "Promoter" : round(promoters / total * 100, 2),
            "Passive" : round(passives / total * 100, 2),
            "Detractor" : round(detractors / total * 100, 2),
            "NPS" : round((promoters - detractors) / total * 100, 2)
        })