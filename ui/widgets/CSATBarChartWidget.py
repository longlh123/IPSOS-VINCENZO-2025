import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as MaxNLocator
import numpy as np

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QAction, QGroupBox, QGridLayout, QComboBox, QHBoxLayout, QSizePolicy
)
from PyQt5.Qt import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class CSATBarChartWidget(QWidget):
    def __init__(self, chart_data, title='', parent=None):
        super().__init__(parent)
        self.title = title
        self.chart_data = chart_data
        layout = QVBoxLayout(self)

        #Remove canvas cũ nếu có
        if hasattr(self, 'canvas'):
            self.layout().removeWidget(self.canvas)
            self.canvas.setParent(None)

        #Create the figure
        self.figure, self.ax = plt.subplots(figsize=(9, 7))
        self.figure.subplots_adjust(left=0.115, right=0.88)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.canvas)

        self.plot_csat_bar_chart()

    def plot_csat_bar_chart(self):
        self.ax.clear()

        products = [ row['product'] for i, row in self.chart_data.iterrows() ]
        sample_sizes = [ row['n'] for i, row in self.chart_data.iterrows() ]
        scores = [ row['p'] for i, row in self.chart_data.iterrows() ]
        changes = [ row['change'] for i, row in self.chart_data.iterrows() ]
        ranks = [ row['rank'] for i, row in self.chart_data.iterrows() ]
        directions = [ row['direction'] for i, row in self.chart_data.iterrows() ]
        
        pos = np.arange(len(products))

        rects = self.ax.barh(pos, scores, color="#e60013", align='center', height=0.5, tick_label=products)

        self.ax.set_xlim([0, 100])
        # self.ax.xaxis.set_major_locator(MaxNLocator(11))
        self.ax.xaxis.grid(True, linestyle='--', which='major', color='gray', alpha=.25)

        for i, (score, n, change, rank, direction) in enumerate(zip(scores, sample_sizes, changes, ranks, directions)):
            #Bar label
            self.ax.text(score - 2, i, f"{int(score)}", va="center", ha="right", color="white", fontweight="bold")

            #Sample Size
            self.ax.text(score + 2, i, f"(n={n})", va="center", ha="left", fontsize=8, color="gray")

            # # Change and direction
            # arrow = "↑" if direction == "up" else ("↓" if direction == "down" else "")
            # color = "green" if direction == "up" else ("red" if direction == "down" else "black")
            # self.ax.text(score + 1, i, f"{change:.2f} {arrow}", va='center', ha='left', fontsize=8, color=color)

            # # Rank
            # if rank:
            #     self.ax.text(score + 10, i, f"#{rank}", va='center', ha='left', fontsize=8, color="#0076a8",
            #                  bbox=dict(boxstyle="round,pad=0.2", facecolor="#d6f0fb", edgecolor="#0076a8"))


        self.ax.set_yticks(pos)
        self.ax.set_yticklabels(products, fontsize=9)
        self.ax.set_xlim(0, max(scores) + 25)
        self.ax.invert_yaxis()  # Highest at top
        self.ax.set_xlabel("CSAT (%)")
        
        if self.title:
            self.ax.set_title(self.title, fontsize=14, fontweight="bold", loc="left", color="#e60013")

        self.figure.tight_layout()
        self.canvas.draw()