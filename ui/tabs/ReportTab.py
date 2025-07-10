import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QAction, QGroupBox, QGridLayout, QComboBox, QHBoxLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.Qt import Qt
from ui.widgets.NPSBarChartWidget import NPSBarChartWidget
from ui.widgets.NPSBarChartDefaultWidget import NPSBarChartDefaultWidget
from ui.widgets.multi_select import MultiSelectWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class ReportTab(QWidget):

    def __init__(self, data=None, dataset=None, filters=None):
        super().__init__()
        
        self.data = data.copy() if data is not None else pd.DataFrame()
        self.dataset = dataset
        
        self.filters = filters
        self.dataset_filters = dataset.get('filters', {})

        #Lưu trữ filter combobox
        self.multiselectitems = {}

        #Create chart data
        self.chart_data = self.create_chart_data()

        # Main layout
        main_layout = QVBoxLayout(self)

        # Create filter group (fixed at top)
        filter_group = self.create_filter_group(self.filters)
        filter_group.setFixedHeight(120)  # optional: adjust as needed
        
        self.set_filters(self.data, self.filters)

        main_layout.addWidget(filter_group)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
            
        # Create a widget for the scroll area
        scroll_content = QWidget()
        scroll_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(15)
        
        if 'filters' in self.dataset.keys():
            dataset_filter_group = self.create_filter_group(self.dataset_filters)
            dataset_filter_group.setFixedHeight(120)  # optional: adjust as needed

            self.set_filters(self.chart_data, self.dataset_filters)

            main_layout.addWidget(dataset_filter_group)

        self.render_chart()

        self.scroll_layout.addStretch() 

        # Set the scroll area widget
        scroll_area.setWidget(scroll_content)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

    def render_chart(self):
        
        filtered_chart_data = self.chart_data.copy()

        for key, values in self.dataset_filters.items():
            multiselectitem = self.multiselectitems[key]
            selected_items = multiselectitem.get_selected_items()

            if len(selected_items) > 0:
                filtered_chart_data = filtered_chart_data[filtered_chart_data[key].isin(selected_items)]

        filtered_chart_data = filtered_chart_data.groupby(self.dataset.get('group_by', [])).apply(self.calculate_nps_components).reset_index()

        for key, values in self.filters.items():
            multiselectitem = self.multiselectitems[key]
            selected_items = multiselectitem.get_selected_items()

            if len(selected_items) > 0:
                filtered_chart_data = filtered_chart_data.loc[filtered_chart_data[key].isin(selected_items)]

        self.clear_layout()

        chart_group = QGroupBox(self.dataset.get('chart_name'))
        chart_group.setMinimumHeight(550)

        layout = QVBoxLayout(chart_group)

        #Create filters của chart
        if self.dataset['chart_type'] == "NPSBarChartDefaultWidget":
            chart_widget = NPSBarChartDefaultWidget(filtered_chart_data)
        if self.dataset['chart_type'] == "NPSBarChartWidget":
            chart_widget = NPSBarChartWidget(filtered_chart_data)

        layout.addWidget(chart_widget)

        self.scroll_layout.addWidget(chart_group)

    def create_filter_group(self, filters):
        groupbox = QGroupBox("Filter")
        
        layout = QVBoxLayout(groupbox)
        
        def create_filter_row(layout, keys: list):
            container = QWidget()

            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)

            for key in keys:
                filter_container = QWidget()

                filter_container_layout = QHBoxLayout(filter_container)
                filter_container_layout.setContentsMargins(0, 0, 0, 0)
                filter_container_layout.setSpacing(5)
                
                label = QLabel(f"{key}")
                filter_container_layout.addWidget(label)

                multiselectitem = MultiSelectWidget(filters[key])

                multiselectitem.selectionChanged.connect(
                    lambda items: self.handle_filter_changed(key, items)
                )

                filter_container_layout.addWidget(multiselectitem)

                self.multiselectitems[key] = multiselectitem

                container_layout.addWidget(filter_container)
            
            layout.addWidget(container)

        keys = list(filters.keys())

        for i in range(0, len(filters.keys()), 2):
            i_from = i 
            i_to = i + 2 if i < len(keys) else i + 1

            create_filter_row(layout, keys[i_from:i_to])

        return groupbox

    def handle_filter_changed(self, column_name: str, value: str):

        # Cập nhật dữ liệu cho tab Report
        self.render_chart()

        print(f"{column_name} changed to {value}")
    
    def set_filters(self, data, filters):
        for column_name in filters.keys():
            filters[column_name] = data[column_name].dropna().unique().tolist()

            self.multiselectitems[column_name].set_items(filters[column_name])

    def create_chart_data(self):
        df = self.data[self.dataset.get('used-cols', [])].copy()

        df = df.rename(columns=self.dataset.get('rename-columns', {}))
        
        df_nps_long = pd.wide_to_long(
            df,
            stubnames=list(self.dataset.get('stubnames', {}).keys()),
            i = self.dataset.get('i-cols', []),
            j = self.dataset.get('j-col', ''),
            sep='###',
            suffix='\\d+'
        )

        df_nps_long = df_nps_long.reset_index().drop(columns=["Order"])

        index_list = self.dataset.get('i-cols', [])
        index_list.append("Q1")

        df_stack = df_nps_long.set_index(index_list).stack().reset_index()
        df_stack.rename(columns={ 'level_5' : 'Product', 0 : 'Score' }, inplace=True)
        df_stack['Product'].replace(self.dataset.get('stubnames', {}), inplace=True)

        df_stack = df_stack.dropna(subset=["Product", "Score"])

        return df_stack

    def calculate_nps_components(self, group):
        total = len(group)

        csat_data = [
            {"product": "Debit Card", "n": 0, "csat": 0, "change": 0.0, "rank": 0, "direction": ""},
            {"product": "Credit Card", "n": 0, "csat": 0, "change": 0.0, "rank": 0, "direction": ""},
            {"product": "Banca", "n": 0, "csat": 0, "change": 0.0, "rank": 0, "direction": ""},
            {"product": "Terms deposit", "n": 0, "csat": 0, "change": 0.0, "rank": 0, "direction": ""},
            {"product": "Bond/Funds", "n": 0, "csat": 0, "change": 0.0, "rank": 0, "direction": ""},
            {"product": "Unsecured loan", "n": 0, "csat": 0, "change": 0.0, "rank": 0, "direction": ""},
            {"product": "Secured loan", "n": 0, "csat": 0, "change": 0.0, "rank": 0, "direction": ""}
        ]

        for product in csat_data:
            n = ((group['Product'] == product.get('product'))).sum()
            csat = round(((group['Product'] == product.get('product')) & (group['Score'] != 'I do not use this bank product')).sum() / total * 100, 2)
            
            product['n'] = n
            product['csat'] = csat
        
        return csat_data


    def clear_layout(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    

    

    
    
    