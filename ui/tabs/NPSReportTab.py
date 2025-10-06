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
from ui.widgets.CSATBarChartWidget import CSATBarChartWidget
from ui.widgets.multi_select import MultiSelectWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from models.chart_mapping import map_chart_data, map_calculation_chart_components

class NPSReportTab(QWidget):

    def __init__(self, data=None, dataset=None):
        super().__init__()
        
        self.data = data.copy() if data is not None else pd.DataFrame()
        self.dataset = dataset
        
        self.filters = dataset.get('main-filters', {})
        self.dataset_filters = dataset.get('dataset-filters', {})

        #Lưu trữ filter multiselection
        self.multiselectitems = {}

        #Lưu trữ filter combobox
        self.comboboxitems = {}

        #Create chart data
        self.chart_data = map_chart_data(self.data, self.dataset)
        
        # Main layout
        main_layout = QVBoxLayout(self)

        # Create filter group (fixed at top)
        filter_group = self.create_filter_group(self.filters)
        # filter_group.setFixedHeight(120)  # optional: adjust as needed
        
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
        
        self.set_filters(self.data, self.filters)

        if 'dataset-filters' in self.dataset.keys():
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
        filtered_chart_data.reset_index(inplace=True)
        
        for key, values in self.filters.items():
            if key in self.multiselectitems:
                multiselectitem = self.multiselectitems[key]
                selected_items = multiselectitem.get_selected_items()
            elif key in self.comboboxitems:
                selected_items = [self.comboboxitems[key].currentText()]

            if len(selected_items) > 0:
                filtered_chart_data = filtered_chart_data.loc[filtered_chart_data[key].isin(selected_items)]

        for key, values in self.dataset_filters.items():
            
            if key in self.multiselectitems:
                multiselectitem = self.multiselectitems[key]
                selected_items = multiselectitem.get_selected_items()
            elif key in self.comboboxitems:
                selected_items = [self.comboboxitems[key].currentText()]

            if len(selected_items) > 0:
                filtered_chart_data = filtered_chart_data[filtered_chart_data[key].isin(selected_items)]

        filtered_chart_data = map_calculation_chart_components(filtered_chart_data, self.dataset)

        self.clear_layout()

        if self.dataset.get('chart', {}).get('type') == 'CSATBarChartWidget':
            banks = filtered_chart_data['Bank'].dropna().unique().tolist()
            
            for bank_name in banks:
                if bank_name != 'None of the above':
                    df = filtered_chart_data[filtered_chart_data['Bank'] == bank_name ]

                    chart_group = self.create_chart_group(bank_name, df, self.dataset.get('chart', {}).get('type'))
                    self.scroll_layout.addWidget(chart_group)
        else:
            chart_group = self.create_chart_group(self.dataset.get('chart', {}).get('title'), filtered_chart_data, self.dataset.get('chart', {}).get('type'))
            self.scroll_layout.addWidget(chart_group)
        
    def create_chart_group(self, title, chart_data, chart_type):
        chart_group = QGroupBox(title)
        chart_group.setMinimumHeight(600)

        if chart_type == "NPSBarChartDefaultWidget":
            layout = QVBoxLayout(chart_group)

            chart_widget = NPSBarChartDefaultWidget(chart_data)
            layout.addWidget(chart_widget)
        if chart_type == "NPSBarChartWidget":
            layout = QVBoxLayout(chart_group)

            chart_widget = NPSBarChartWidget(self.dataset.get('chart', {}), chart_data)
            layout.addWidget(chart_widget)
        if chart_type == "CSATBarChartWidget":
            layout = QVBoxLayout(chart_group)

            chart_widget = CSATBarChartWidget(chart_data)
            layout.addWidget(chart_widget)

        return chart_group

    def create_filter_group(self, filters):
        groupbox = QGroupBox("Filter")
        
        layout = QGridLayout(groupbox)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        
        def create_filter_row(row, keys: list):
            row, col = row, 0

            for key in keys:
                label = QLabel(f"{key}")
                layout.addWidget(label, row, col)

                if isinstance(filters[key], str):
                    comboboxitem = QComboBox()
                     
                    comboboxitem.currentTextChanged.connect(
                        lambda text: self.handle_filter_changed(key, text)
                    )

                    layout.addWidget(comboboxitem, row, col + 1)

                    self.comboboxitems[key] = comboboxitem
                elif isinstance(filters[key], list):
                    multiselectitem = MultiSelectWidget(filters[key])

                    multiselectitem.selectionChanged.connect(
                        lambda items: self.handle_filter_changed(key, items)
                    )

                    layout.addWidget(multiselectitem, row, col + 1)

                    self.multiselectitems[key] = multiselectitem

                col = col + 2

        keys = list(filters.keys())

        for i in range(0, len(filters.keys()), 2):
            i_from = i 
            i_to = i + 2 if i < len(keys) else i + 1

            create_filter_row(i, keys[i_from:i_to])

        return groupbox

    def handle_filter_changed(self, column_name: str, value: str):

        # Cập nhật dữ liệu cho tab Report
        self.render_chart()

        print(f"{column_name} changed to {value}")
    
    def set_filters(self, data, filters):
        for column_name in filters.keys():
            filters[column_name] = data[column_name].dropna().unique().tolist()

            if column_name in self.multiselectitems:
                self.multiselectitems[column_name].set_items(filters[column_name])
            elif column_name in self.comboboxitems:
                self.comboboxitems[column_name].clear()
                self.comboboxitems[column_name].addItems(filters[column_name])
                self.comboboxitems[column_name].setCurrentIndex(0)

    def clear_layout(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

            


    

    
    
    