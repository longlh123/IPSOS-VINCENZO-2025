from charts.base_renderer import BaseChartRenderer
import numpy as np

class CSATBarChartRenderer(BaseChartRenderer):
    def render(self):
        df = self.data

        yAxis_1_categories = self.config['yAxis'].get('categories')

        yAxis_1_items = list(df[self.group_by[0]].unique())

        yAxis_1_categories = [cat for cat in yAxis_1_categories if cat in yAxis_1_items]

        if len(self.group_by) > 1:
            subset_name = self.group_by[1]
            yAxis_2_categories = sorted(df[subset_name].unique())
        
        colors = self.config['style'].get('colors')

        bar_width = 0.3
        bar_gap = 0.1
        group_width = (bar_width + bar_gap) * len(yAxis_2_categories) + 0.3
        x_base = np.arange(len(yAxis_1_categories)) * group_width
        
        for i, wave in enumerate(yAxis_2_categories):
            subset = df[df[subset_name] == wave].set_index("Bank").reindex(yAxis_1_categories).reset_index()

            x_pos = x_base + i * (bar_width + bar_gap)
            x_bottom = np.zeros(len(x_pos))

            for j, cat in enumerate(self.config['xAxis'].get('categories')):
                p = subset[cat].fillna(0)

                self.ax.bar(x_pos, p, bar_width, bottom=x_bottom, color=colors[j], label=f"{cat}" if i == 0 else None)

                if j == 0:
                    for xi, pi, xb in zip(x_pos, p, x_bottom):
                        if pi > 0:
                            self.ax.text(xi, xb + pi / 2, f"{pi:.0f}%", ha="center", va="center", fontsize=8, color="white")

                x_bottom += p
            
            for xi in x_pos:
                self.ax.text(xi, -10, wave, ha="center", va="center", fontsize=8)

        self.ax.set_xticks(x_base + bar_width / 2)
        self.ax.set_xticklabels(yAxis_1_categories, rotation=45, ha='right', fontsize=9)
        self.ax.set_ylim(-15, 110)
        self.ax.set_ylabel("Percentage")
        self.ax.set_title(self.config.get('title'))
        self.ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        
        return self.fig