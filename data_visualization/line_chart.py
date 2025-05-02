import matplotlib.pyplot as plt

from utils.utils import load_csv


class LineChart:
    def __init__(self, df):
        self.df = df

    def plot_line_chart(self):
        plt.figure(figsize=(14, 8))
        plt.plot(self.df.index, self.df['Close'], label='Close Price', color='b')
        plt.title('Line Chart')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    sample_data = load_csv("AAVE_USD_FOR_LINE_CHART.csv")

    line_chart = LineChart(sample_data)
    line_chart.plot_line_chart()
