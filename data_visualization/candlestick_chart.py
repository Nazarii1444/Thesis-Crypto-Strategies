import mplfinance as mpf

from utils.utils import load_csv


class CandlestickChart:
    def __init__(self, df):
        self.df = self.prepare_data(df)

    @staticmethod
    def prepare_data(df):
        df = df.copy()
        df = df[['Open', 'High', 'Low', 'Close']]
        return df

    def plot_candlestick_chart(self):
        """Plot candlestick chart using mplfinance."""
        mpf.plot(
            self.df,
            type='candle',
            style='charles',
            title='Candlestick Chart',
            ylabel='Price',
            figsize=(14, 8),
            tight_layout=True
        )


if __name__ == "__main__":
    sample_data = load_csv("AAVE_USD_FOR_CANDLESTICK_CHART.csv")

    line_chart = CandlestickChart(sample_data)
    line_chart.plot_candlestick_chart()
