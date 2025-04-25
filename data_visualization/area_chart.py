import plotly.express as px

from utils.loader import load_csv


class AreaChart:
    def __init__(self, df):
        self.df = df

    def plot_area_chart(self):
        fig = px.area(self.df, x=self.df.index, y='Close', title='Area Chart')
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Price',
            margin=dict(l=15, r=15, t=50, b=15),
            width=800,
            height=400
        )
        fig.show()


if __name__ == "__main__":
    sample_data = load_csv("AAVE_USD_FOR_AREA_CHART.csv")
    area_chart = AreaChart(sample_data)
    area_chart.plot_area_chart()
