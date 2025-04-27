import os
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from pandas import DataFrame

from config import logger
from time_it import time_it

TICKERS = [
    # '1INCH-USD',
    'AAVE-USD',
    # 'PEOPLE-USD',
    # 'ADA-USD',
    # 'ALGO-USD', 'ANKR-USD', 'ATOM-USD',
    # 'AUDIO-USD', 'AVAX-USD', 'AXS-USD',
    # 'BAL-USD', 'BCH-USD', 'BNB-USD',
    # 'BTC-USD', 'BTT-USD', 'CAKE-USD',
    # 'CHZ-USD', 'CRO-USD', 'CRV-USD',
    # 'CVC-USD', 'DOGE-USD', 'DOT-USD',
    # 'EGLD-USD', 'ENJ-USD', 'ETC-USD',
    # 'ETH-USD', 'FIL-USD', 'FTM-USD',
    # 'FTT-USD', 'GALA-USD', 'HBAR-USD',
    # 'HNT-USD', 'IOST-USD', 'KSM-USD',
    # 'LINK-USD', 'MANA-USD', 'MATIC-USD',
    # 'NEAR-USD', 'OMG-USD', 'QTUM-USD',
    # 'REN-USD', 'RUNE-USD', 'RVN-USD',
    # 'SAND-USD', 'SC-USD', 'SNX-USD',
    # 'SOL-USD', 'STORJ-USD', 'THETA-USD',
    # 'UNI-USD', 'VET-USD', 'XEM-USD',
    # 'XMR-USD', 'XRP-USD', 'XTZ-USD',
    # 'YFI-USD', 'ZEN-USD', 'ZIL-USD',
    # 'ZRX-USD', 'BONK-USD'
]

INTERVALS = [
    # ("one_m", "one_m_data_downloader"),
    # ("two_m", "two_m_data_downloader"),
    ("five_m", "five_m_data_downloader"),
    # ("fifteen_m", "fifteen_m_data_downloader"),
    # ("thirty_m", "thirty_m_data_downloader"),
    # ("one_h", "one_h_data_downloader"),
    # ("one_d", "one_d_data_downloader"),
    # ("five_d", "five_d_data_downloader"),  # uncomment these to download five_d, one_w, one_mo, three_mo
    # ("one_w", "one_w_data_downloader"),
    # ("one_mo", "one_mo_data_downloader"),
    # ("three_mo", "three_mo_data_downloader")
]
SIXTY_DAYS_TIMEFRAMES = ["2m", "5m", "15m", "30m", "1h", "1d"]
MAPPER = {
    "2m": "two_m",
    "5m": "five_m",
    "15m": "fifteen_m",
    "30m": "thirty_m",
    "1h": "one_h",
    "1d": "one_d"
}

INFINITE = -1

AVAILABILITY = {  # Max availability for the interval
    "1m": 30,
    "2m": 60, "5m": 60, "15m": 60, "30m": 60, "90m": 60,
    "60m": 730, "1h": 730,
    "1d": INFINITE, "5d": INFINITE, "1wk": INFINITE, "1mo": INFINITE, "3mo": INFINITE
}

# Intervals available for downloading for the last 60 days
AVAILABILITY_FOR_SIXTY_DAYS = ["2m", "5m", "15m", "30m", "90m", "60m", "1h", "1d"]
RANGE_AVAILABLE_INTERVALS = ["2m", "5m", "15m", "30m", "1h"]  # Not available for downloading MAX period
MAX_DOWNLOADER_AVAILABLE_INTERVALS = ["1d", "5d", "1wk", "1mo", "3mo"]  # Available for downloading MAX period


class YFDownloader:
    """
    =============================== YFINANCE INFO ===============================
    Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]

    === MAX Availability ===
    1m - last 30d
    2m - last 60d
    5m - last 60d
    15m - last 60d
    60m - last 730d
    90m - last 60d
    1h - last 730d
    1d 5d 1wk 1mo 3mo - no limit

    ======================================================================================================

    Difference between max_downloader and availability_range_downloader methods:
    max_downloader - downloads data from yfinance at maximum available interval (60 or 730 days)
    availability_range_downloader - downloads data from yfinance at maximum available interval (INFINITE)

    ======================================================================================================

    === 60 days Availability ===
    1m - last 30d
    2m, 5m, 15m, 60m, 90m, 1h, 1d 5d 1wk 1mo 3mo - last 60d
    ======================================================================================================
    """

    def __init__(self, symbol: str = "BTC-USD"):
        self.symbol = symbol

    def __repr__(self):
        return f'<Downloader(symbol="{self.symbol}") Id={id(self)} at {hex(id(self))})>'

    @staticmethod
    def download_data(symbol, current_date, next_date, interval: str = "1m"):
        data = yf.download(
            tickers=symbol,
            start=current_date.strftime("%Y-%m-%d"),
            end=next_date.strftime("%Y-%m-%d"),
            interval=interval
        )
        return data

    @staticmethod
    def download_data_minutes(symbol, current_date, next_date, interval: str = "1m"):
        data = yf.download(
            tickers=symbol,
            start=current_date.strftime("%Y-%m-%d %H:%M"),
            end=next_date.strftime("%Y-%m-%d %H:%M"),
            interval=interval
        )
        return data

    @staticmethod
    def download_max(symbol, interval: str):
        data = yf.download(
            tickers=symbol,
            period="max",
            interval=interval
        )
        return data

    @staticmethod
    def download_last_sixty_days(symbol, interval: str):
        end = datetime.today()
        start = end - timedelta(days=59)
        data = yf.download(
            tickers=symbol, interval=interval,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
        )
        return data

    def one_m_data_downloader(self) -> DataFrame:
        """Wild things are going on here, but it works"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=29)
        data_frames = []

        # 7-day intervals for the first 28 days
        for _ in range(4):
            next_date = start_date + timedelta(days=7)
            data = self.download_data(self.symbol, start_date, next_date)
            data_frames.append(data)
            start_date = next_date

        # Remaining 1-day interval to complete 29 days
        data = self.download_data(self.symbol, start_date, end_date)
        data_frames.append(data)

        final_data = pd.concat(data_frames)
        final_data.reset_index(inplace=True)
        logger.debug("\n" + final_data.head(2).to_string())
        return final_data

    def two_m_data_downloader(self) -> DataFrame:
        return self.availability_range_downloader("2m")

    def five_m_data_downloader(self) -> DataFrame:
        return self.availability_range_downloader("5m")

    def fifteen_m_data_downloader(self) -> DataFrame:
        return self.availability_range_downloader("15m")

    def thirty_m_data_downloader(self) -> DataFrame:
        return self.availability_range_downloader("30m")

    def one_h_data_downloader(self) -> DataFrame:
        return self.availability_range_downloader("1h")

    def one_d_data_downloader(self) -> DataFrame:
        return self.max_downloader("1d")

    def five_d_data_downloader(self) -> DataFrame:
        return self.max_downloader("5d")

    def one_w_data_downloader(self) -> DataFrame:
        return self.max_downloader("1wk")

    def one_mo_data_downloader(self) -> DataFrame:
        return self.max_downloader("1mo")

    def three_mo_data_downloader(self) -> DataFrame:
        return self.max_downloader("3mo")

    def availability_range_downloader(self, interval: str) -> DataFrame:
        """
        Method is used only inside current class, no external usages
        Possible interval parameter - any of available_intervals
        """
        if interval not in RANGE_AVAILABLE_INTERVALS:
            raise ValueError(f"Invalid period: {interval}")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=AVAILABILITY[interval] - 1)
        logger.info(f"START: {start_date} END: {end_date}")

        data = self.download_data(self.symbol, start_date, end_date, interval)
        data.reset_index(inplace=True)
        logger.info("\n" + data.head(2).to_string())
        return data

    def max_downloader(self, interval: str) -> DataFrame:
        """
        Method is used only inside current class, no external usages
        Possible interval parameter - any of available_intervals
        """
        if interval not in MAX_DOWNLOADER_AVAILABLE_INTERVALS:
            raise ValueError(f"Invalid period: {interval}")

        data = self.download_max(self.symbol, interval)
        data.reset_index(inplace=True)
        logger.info("\n" + data.head(2).to_string())
        return data

    def last_sixty_days_downloader(self, interval: str = "5m") -> DataFrame:
        if interval not in AVAILABILITY_FOR_SIXTY_DAYS:
            raise ValueError(f"Interval {interval} is not available for 60 days downloading.")

        data = self.download_last_sixty_days(self.symbol, interval)
        data.reset_index(inplace=True)
        return data


class YFDataGenerator:
    @staticmethod
    def generate_all_data():
        for interval_name, downloader_method in INTERVALS:
            YFDataGenerator.generate_data(interval_name, downloader_method)

    @staticmethod
    def generate_data(interval_name: str, downloader_method: str):
        folder_path = f'../{interval_name}'
        os.makedirs(folder_path, exist_ok=True)

        for ticker in TICKERS:
            downloader = YFDownloader(ticker)
            data = getattr(downloader, downloader_method)()
            file_path = os.path.join(folder_path, f'{ticker.replace("-", "_")}.csv')
            data.to_csv(file_path, index=False, sep=',', encoding='utf-8')

    @staticmethod
    def generate_sixty_days_data():
        """
        Generates 60 days data for every ticker and interval listed in SIXTY_DAYS_TIMEFRAMES.
        Creates a folder for each interval and saves the data as CSV files.
        """
        for interval in SIXTY_DAYS_TIMEFRAMES:
            folder_path = f'../csvs/{MAPPER[interval]}'
            os.makedirs(folder_path, exist_ok=True)

            for ticker in TICKERS:
                downloader = YFDownloader(ticker)
                try:
                    data = downloader.last_sixty_days_downloader(interval)
                    file_path = os.path.join(folder_path, f'{ticker.replace("-", "_")}.csv')
                    data.to_csv(file_path, index=False, sep=',', encoding='utf-8')
                    # log_info(f'{ticker} data for interval {interval} generated!')
                except ValueError as e:
                    ...
            # log_error(f"Error generating data for {ticker} at interval {interval}: {e}")

            # log_info(f'{interval.replace("_", " ")} data generation complete!')


@time_it
def generate_all_data():
    """Generates all data with MAX interval possible for every timeframe."""
    YFDataGenerator().generate_all_data()


@time_it
def generate_sixty_days_data():
    """Generates 60 days data with for every timeframe."""
    YFDataGenerator().generate_sixty_days_data()


if __name__ == '__main__':
    generate_all_data()
