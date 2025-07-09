import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QAction, QGroupBox, QGridLayout, QComboBox, QHBoxLayout
)
from PyQt5.Qt import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class NPSBarChartDefaultWidget(QWidget):
    def __init__(self, chart_data, parent=None):
        super().__init__(parent)
        self.chart_data = chart_data
        layout = QVBoxLayout(self)

        #Remove canvas cũ nếu có
        if hasattr(self, 'canvas'):
            self.layout().removeWidget(self.canvas)
            self.canvas.setParent(None)
            
        #Xét chiều rộng canvas
        fig_width = 2 + len(self.chart_data["Wave"].unique()) * 2

        self.figure, self.ax = plt.subplots(figsize=(fig_width, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.plot_nps_bar_chart()

    def plot_nps_bar_chart(self):
        ax = self.ax
        ax.clear()

        waves = sorted(self.chart_data["Wave"].unique())

        wave_count = len(waves)

        #Khoảng cách giữa các nhóm
        bar_width = 0.5
        x = np.arange(len(waves))
        
        colors = ["#008a3e", "#ffc000", "#7f7f7f"]

        promoter = []
        passive = []
        detractor = []
        nps = []

        for i, wave in enumerate(waves):
            subset = self.chart_data[self.chart_data["Wave"] == wave]

            promoter.append(subset["Promoter"].fillna(0).iloc[0])
            passive.append(subset["Passive"].fillna(0).iloc[0])
            detractor.append(subset["Detractor"].fillna(0).iloc[0])
            nps.append(subset["NPS"].fillna(0).round(0).astype(int).iloc[0])

        promoter = np.array(promoter)
        passive = np.array(passive)
        detractor = np.array(detractor)
        nps = np.array(nps)

        ax.bar(x, detractor, bar_width, color=colors[2], label=f"Detractor")
        ax.bar(x, passive, bar_width, bottom=detractor, color=colors[1], label=f"Passive")
        ax.bar(x, promoter, bar_width, bottom=detractor + passive, color=colors[0], label=f"Promoter")

        for xi, p in zip(x, promoter):
            if p > 0:
                ax.text(xi, p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="white")
        
        for xi, p, base in zip(x, passive, detractor):
            if p > 0:
                ax.text(xi, base + p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="black")

        # Vẽ label NPS trên cùng
        for xi, y_top, nps_val in zip(x, promoter + passive + detractor, nps):
            ax.text(xi, y_top + 5, f"{nps_val}", ha="center", va="center", fontsize=9, color="white",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="red", edgecolor="none"))

        ax.set_xticks(x)
        ax.set_xticklabels(waves, rotation=0, ha='right', fontsize=9)
        ax.set_ylim(-15, 110)
        ax.set_ylabel("Percentage")
        ax.set_title("NPS Breakdown by Wave")
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        self.figure.tight_layout()
        self.canvas.draw()