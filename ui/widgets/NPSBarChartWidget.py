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

class NPSBarChartWidget(QWidget):
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

        banks = list(self.chart_data["Q1"].unique())
        waves = sorted(self.chart_data["Wave"].unique())

        group_count = len(banks)
        wave_count = len(waves)

        #Khoảng cách giữa các nhóm
        bar_width = 0.3
        bar_gap = 0.1
        group_width = (bar_width + bar_gap) * wave_count + 0.3

        x_base = np.arange(group_count) * group_width

        colors = ["#008a3e", "#ffc000", "#7f7f7f"]

        for i, wave in enumerate(waves):
            subset = self.chart_data[self.chart_data["Wave"] == wave].set_index("Q1").reindex(banks).reset_index()

            promoter = subset["Promoter"].fillna(0)
            passive = subset["Passive"].fillna(0)
            detractor = subset["Detractor"].fillna(0)
            nps = subset["NPS"].fillna(0).round(0).astype(int)

            x_pos = x_base + i * (bar_width + bar_gap)
            
            ax.bar(x_pos, detractor, bar_width, color=colors[2], label=f"{wave} - Detractor" if i == 0 else None)
            ax.bar(x_pos, passive, bar_width, bottom=detractor, color=colors[1], label=f"{wave} - Passive" if i == 0 else None)
            ax.bar(x_pos, promoter, bar_width, bottom=detractor + passive, color=colors[0], label=f"{wave} - Promoter" if i == 0 else None)

            for xi, p in zip(x_pos, promoter):
                if p > 0:
                    ax.text(xi, p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="white")
            
            for xi, p, base in zip(x_pos, passive, detractor):
                if p > 0:
                    ax.text(xi, base + p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="black")

            for xi, yi in zip(x_pos, nps):
                y_top = promoter[i] + passive[i] + detractor[i] + 5

                ax.text(xi, y_top, f"{yi}", ha="center", va="center", fontsize=9, color="white",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="red", edgecolor="none"))

            for xi in x_pos:
                ax.text(xi, -10, wave, ha="center", va="center", fontsize=8)

        ax.set_xticks(x_base + bar_width / 2)
        ax.set_xticklabels(banks, rotation=45, ha='right', fontsize=9)
        ax.set_ylim(-15, 110)
        ax.set_ylabel("Percentage")
        ax.set_title("NPS Breakdown by Bank and Wave")
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        self.figure.tight_layout()
        self.canvas.draw()