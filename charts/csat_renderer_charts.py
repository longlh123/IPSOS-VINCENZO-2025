from .base_renderer import BaseChartRenderer
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class CSATBarChartsRenderer(BaseChartRenderer):
    def render(self):
        self.data_temp = self.data[["Wave", "Bank", "category", "p"]]
        data = {
            "Bank": self.data["Bank"].tolist(),
            "Product": self.config['yAxis']['categories'] * 6,
            "CSAT": self.data["p"].tolist()  
        }

        df = pd.DataFrame(data)

        # 🔹 Vẽ 7 chart nằm ngang 1 hàng
        g = sns.catplot(
            data=df,
            x="CSAT",
            y="Product",
            col="Bank",
            kind="bar",
            col_wrap=7,      # 7 chart trên 1 hàng
            sharex=True,     # cùng scale trục X
            sharey=True,     # cùng scale trục Y
            height=4,        # chiều cao mỗi chart
            aspect=0.7,      # tỉ lệ rộng/cao
            color="red"      # giống style bạn đã có
        )

        g.set_titles("{col_name}")  # chỉ hiện tên ngân hàng
        g.set_axis_labels("CSAT (%)", "Product")
        
        #Annotate số % trên từng bar
        for ax in g.axes.flat:
            ax.set_xlim(0, 100)
            ax.set_xticks([0, 25, 50, 75, 100])
            
            for p in ax.patches:
                width = p.get_width()

                if width > 0:
                    ax.text(
                        width + 1, #Vị trí của x: lệch sang trái một chút
                        p.get_y() + p.get_height() / 2, #Vị trí y giữa bar
                        f"{width:.0f}%",
                        va="center"
                    )

        fig = g.figure

        return fig