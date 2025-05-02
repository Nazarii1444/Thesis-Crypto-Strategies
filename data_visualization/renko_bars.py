import matplotlib.pyplot as plt
import pandas as pd

from utils.utils import load_csv


class Renko:
    def __init__(self, df, brick_size):
        """
        Initialize Renko chart with dataframe and brick size

        Parameters:
        df (pandas.DataFrame): DataFrame with OHLC data
        brick_size (float): Size of each Renko brick
        """
        self.df = df.copy()
        self.brick_size = brick_size
        self.renko_prices = []
        self.renko_directions = []
        self.timestamps = []

    def calculate_renko(self):
        """Calculate Renko bars from price data"""
        prices = self.df['Close'].values
        dates = self.df.index

        # Initialize first brick
        current_price = prices[0]
        self.renko_prices.append(current_price - (current_price % self.brick_size))
        self.renko_directions.append(0)
        self.timestamps.append(dates[0])

        for i, price in enumerate(prices[1:], 1):
            diff = price - self.renko_prices[-1]
            num_bricks = int(diff / self.brick_size)

            if abs(num_bricks) >= 1:
                for j in range(abs(num_bricks)):
                    if num_bricks > 0:
                        new_price = self.renko_prices[-1] + self.brick_size
                        direction = 1
                    else:
                        new_price = self.renko_prices[-1] - self.brick_size
                        direction = -1

                    self.renko_prices.append(new_price)
                    self.renko_directions.append(direction)
                    self.timestamps.append(dates[i])

        return pd.DataFrame({
            'Date': self.timestamps,
            'Price': self.renko_prices,
            'Direction': self.renko_directions
        }).set_index('Date')

    def plot_renko(self):
        renko_data = self.calculate_renko()
        fig, ax = plt.subplots(figsize=(15, 7))

        # Plot bars
        for i in range(len(renko_data)):
            color = 'green' if renko_data['Direction'].iloc[i] == 1 else 'red' if renko_data['Direction'].iloc[
                                                                                      i] == -1 else 'gray'
            ax.add_patch(plt.Rectangle(
                (i, renko_data['Price'].iloc[i] - self.brick_size),
                0.8,  # width
                self.brick_size,  # height
                color=color,
                alpha=0.7
            ))

        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_title("Renko Chart - Trading Data Example", fontsize=14, pad=20)
        ax.set_xlabel('Number of Bricks', fontsize=12)
        ax.set_ylabel('Price', fontsize=12)

        ax.set_xlim(-1, len(renko_data) + 1)
        ax.set_ylim(
            min(renko_data['Price']) - 2 * self.brick_size,
            max(renko_data['Price']) + 2 * self.brick_size
        )

        plt.tight_layout()
        return plt


if __name__ == "__main__":
    sample_data = load_csv("AAVE_USD_FOR_BAR_CHART.csv")
    renko = Renko(sample_data, brick_size=0.25)

    plt = renko.plot_renko()
    plt.show()
