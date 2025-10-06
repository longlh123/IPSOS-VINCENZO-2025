from charts.base_renderer import BaseChartRenderer
import numpy as np

class NPSBarChartDefaultRenderer(BaseChartRenderer):
    def render(self):
        df = self.data
        waves = sorted(df["Wave"].unique())
        colors = self.config['style'].get('colors')

        bar_width = 0.5
        x_base = np.arange(len(waves))
        
        promoter = []
        passive = []
        detractor = []
        nps = []

        for i, wave in enumerate(waves):
            subset = df[df["Wave"] == wave]

            promoter.append(subset["Promoter"].fillna(0).iloc[0])
            passive.append(subset["Passive"].fillna(0).iloc[0])
            detractor.append(subset["Detractor"].fillna(0).iloc[0])
            nps.append(subset["NPS"].fillna(0).round(0).astype(int).iloc[0])

        promoter = np.array(promoter)
        passive = np.array(passive)
        detractor = np.array(detractor)
        nps = np.array(nps)

        self.ax.bar(x_base, detractor, bar_width, color=colors[2], label=f"Detractor")
        self.ax.bar(x_base, passive, bar_width, bottom=detractor, color=colors[1], label=f"Passive")
        self.ax.bar(x_base, promoter, bar_width, bottom=detractor + passive, color=colors[0], label=f"Promoter")

        for xi, p in zip(x_base, promoter):
            if p > 0:
                self.ax.text(xi, p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="white")
        
        for xi, p, base in zip(x_base, passive, detractor):
            if p > 0:
                self.ax.text(xi, base + p / 2, f"{p:.0f}%", ha="center", va="center", fontsize=8, color="black")

        # Vẽ label NPS trên cùng
        for xi, y_top, nps_val in zip(x_base, promoter + passive + detractor, nps):
            self.ax.text(xi, y_top + 5, f"{nps_val}", ha="center", va="center", fontsize=9, color="white",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="red", edgecolor="none"))

        self.ax.set_xticks(x_base)
        self.ax.set_xticklabels(waves, rotation=0, ha='right', fontsize=9)
        self.ax.set_ylim(-15, 110)
        self.ax.set_ylabel("Percentage")
        self.ax.set_title("NPS Breakdown by Wave")
        self.ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        
        return self.fig