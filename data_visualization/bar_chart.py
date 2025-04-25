import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

from utils.loader import load_csv


class OHLCBarChart:
    def __init__(self, df):
        self.df = self.prepare_data(df)

    @staticmethod
    def prepare_data(df):
        df = df.copy()
        df = df[['Open', 'High', 'Low', 'Close']]
        return df

    def plot_ohlc_chart(self):
        """Plot OHLC bar chart using mplfinance."""
        mpf.plot(self.df, type='ohlc', style='charles', title='OHLC Bar Chart', ylabel='Price', figsize=(12, 7), tight_layout=True)


if __name__ == "__main__":
    sample_data = load_csv("AAVE_USD_FOR_BAR_CHART.csv")
    ohlc_chart = OHLCBarChart(sample_data)
    ohlc_chart.plot_ohlc_chart()
