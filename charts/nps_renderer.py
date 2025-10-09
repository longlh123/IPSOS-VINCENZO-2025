from charts.base_renderer import BaseChartRenderer
import numpy as np
import pandas as pd


class NPSBarChartRenderer(BaseChartRenderer):
    def render(self):
        df = self.data

        yAxis_1_categories = self.config['yAxis'].get('categories')

        yAxis_1_items = list(df[self.group_by[0]].unique())

        yAxis_1_categories = [cat for cat in yAxis_1_categories if cat in yAxis_1_items]

        if len(self.group_by) > 1:
            subset_name = self.group_by[1]

            df['wave_parsed'] = df[subset_name].apply(self.parse_wave_or_quarter)
            df_sorted = df.sort_values('wave_parsed')

            yAxis_2_categories = df_sorted[subset_name].unique()
        
        colors = self.config['style'].get('colors')

        bar_width = 0.3
        bar_gap = 0.1
        group_width = (bar_width + bar_gap) * len(yAxis_2_categories) + 0.3
        x_base = np.arange(len(yAxis_1_categories)) * group_width
        
        for i, wave in enumerate(yAxis_2_categories):
            subset = df[df[subset_name] == wave].set_index("Bank").reindex(yAxis_1_categories).reset_index()

            promoter = subset["Promoter"].fillna(0)
            passive = subset["Passive"].fillna(0)
            detractor = subset["Detractor"].fillna(0)
            nps = subset["NPS"].fillna(0).round(0).astype(int)

            x_pos = x_base + i * (bar_width + bar_gap)
            
            self.ax.bar(x_pos, detractor, bar_width, color=colors[2], label=f"{wave} - Detractor" if i == 0 else None)
            self.ax.bar(x_pos, passive, bar_width, bottom=detractor, color=colors[1], label=f"{wave} - Passive" if i == 0 else None)
            self.ax.bar(x_pos, promoter, bar_width, bottom=detractor + passive, color=colors[0], label=f"{wave} - Promoter" if i == 0 else None)
            
            for xi, p, base in zip(x_pos, passive, detractor):
                if p > 0:
                    self.ax.text(xi, base + p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="black")

            for xi, p, base_1, base_2 in zip(x_pos, promoter, detractor, passive):
                if p > 0:
                    self.ax.text(xi, base_1 + base_2 + p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="white")

            for j, (xi, yi) in enumerate(zip(x_pos, nps)):
                y_top = promoter[j] + passive[j] + detractor[j] + 5

                self.ax.text(xi, y_top, f"{yi}", ha="center", va="center", fontsize=9, color="white",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="red", edgecolor="none"))

            for xi in x_pos:
                self.ax.text(xi, -10, wave, ha="center", va="center", fontsize=8)

        self.ax.set_xticks(x_base + bar_width / 2)
        self.ax.set_xticklabels(yAxis_1_categories, rotation=45, ha='right', fontsize=9)
        self.ax.set_ylim(-15, 110)
        self.ax.set_ylabel("Percentage")
        self.ax.set_title("NPS Breakdown by Bank and Wave")
        self.ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        
        return self.fig
    
    def parse_wave_or_quarter(self, x):
        x = x.strip()
        y = x.split("'")

        if y[0] == 'Q1' and y[1] == '25':
            x = x.replace('Q1', 'Jan')
        
        return pd.to_datetime(x.replace("'", ""), format="%b%y", errors="coerce")
    

