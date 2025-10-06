import matplotlib.pyplot as plt

class BaseChartRenderer:
    def __init__(self, data, config, group_by):
        self.data = data
        self.config = config
        self.group_by = group_by
        self.fig, self.ax = plt.subplots()

    def render(self):
        raise NotImplementedError("SubClasses must implement render()")
    
    def get_figure(self):
        return self.fig
    