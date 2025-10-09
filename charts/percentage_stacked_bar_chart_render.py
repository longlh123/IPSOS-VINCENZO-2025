from charts.base_renderer import BaseChartRenderer
import numpy as np
import pandas as pd

class PercentageStackedBarChartRenderer(BaseChartRenderer):
    def render(self):
        df = self.data.copy()

        # ---- Setup ----
        xAxis_label = self.config['xAxis'].get('label', 'CSAT_Score')
        xAxis_categories = self.config['xAxis'].get('categories', [])
        colors = self.config['style'].get('colors', [])
        title = self.config.get('title', 'CSAT Chart')

        yAxis_label = self.config['yAxis'].get('label', 'Wave')

        df['wave_parsed'] = df[self.group_by[0]].apply(self.parse_wave_or_quarter)
        df_sorted = df.sort_values('wave_parsed')

        yAxis_categories = df_sorted[self.group_by[0]].unique()  # ["Apr'25", "May'25", "Q1'25"]

        bar_width = 0.5
        x_pos = np.arange(len(yAxis_categories))

        # ---- Draw chart ----
        x_bottom = np.zeros(len(x_pos))

        for j, cat in enumerate(xAxis_categories):
            p = df[cat].fillna(0)

            # Vẽ stacked bar
            self.ax.bar(
                x_pos, p, bar_width, bottom=x_bottom,
                color=colors[j], label=f"{cat}"
            )

            # Thêm label % cho từng tầng
            for xi, pi, xb in zip(x_pos, p, x_bottom):
                if pi > 0:
                    self.ax.text(
                        xi, xb + pi / 2,
                        f"{pi:.0f}%", ha="center", va="center",
                        fontsize=8, color="white"
                    )

            x_bottom += p

        # ---- X-axis ----
        self.ax.set_xticks(x_pos)
        self.ax.set_xticklabels(yAxis_categories, rotation=0, ha='center', fontsize=9)

        # ---- Styling ----
        self.ax.set_ylim(0, 110)
        self.ax.set_ylabel("Percentage")
        self.ax.set_title(title)
        self.ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

        return self.fig

    def parse_wave_or_quarter(self, x):
        x = x.strip()
        y = x.split("'")

        if y[0] == 'Q1' and y[1] == '25':
            x = x.replace('Q1', 'Jan')
        
        return pd.to_datetime(x.replace("'", ""), format="%b%y", errors="coerce")