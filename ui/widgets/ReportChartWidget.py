from PyQt5.QtWidgets import ( QWidget, QVBoxLayout, QSizePolicy )
from PyQt5.Qt import Qt
from charts.registry import create_renderer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class ReportChartWidget(QWidget):
    def __init__(self, chart_data, chart_config: dict, group_by: list, parent=None):
        super().__init__(parent)

        renderer = create_renderer(chart_data, chart_config, group_by)
        fig = renderer.render()
        
        layout = QVBoxLayout(self)

        #Remove canvas cũ nếu có
        if hasattr(self, 'canvas'):
            self.layout().removeWidget(self.canvas)
            self.canvas.setParent(None)
            
        #Xét chiều rộng canvas
        self.canvas = FigureCanvas(fig)

        self.canvas.setMinimumSize(1200, 400)   # kích thước tối thiểu
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        plt.close(fig)

        layout.addWidget(self.canvas)