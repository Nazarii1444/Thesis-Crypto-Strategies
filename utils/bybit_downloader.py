import os
import time
from datetime import datetime

import pandas as pd
import requests

from utils import time_it

INTERVAL_MAP = {
    "1m": "one_m",
    "2m": "two_m",
    "5m": "five_m",
    "15m": "fifteen_m",
    "30m": "thirty_m",
    "1h": "one_h",
    "2h": "two_h",
    "4h": "four_h",
    "6h": "six_h",
    "1d": "one_d",
    "1w": "one_w",
}

interval_to_milliseconds = {
    '1m': 60_000,
    '3m': 3 * 60_000,
    '5m': 5 * 60_000,
    '15m': 15 * 60_000,
    '30m': 30 * 60_000,
    '1h': 60 * 60_000,
    '2h': 2 * 60 * 60_000,
    '4h': 4 * 60 * 60_000,
    '6h': 6 * 60 * 60_000,
    '8h': 8 * 60 * 60_000,
    '12h': 12 * 60 * 60_000,
    '1d': 24 * 60 * 60_000,
    '1w': 7 * 24 * 60 * 60_000,
}

valid_intervals = {
    '1m': 1,
    '3m': 3,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '1h': 60,
    '4h': 240,
    '1d': 'D',
    '1w': 'W'
}


class BybitKlinesLoader:
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.valid_categories = {"linear", "inverse", "spot"}
        self.columns = ["Datetime", "Open", "High", "Low", "Close", "Volume", "Turnover"]

    @staticmethod
    def datetime_to_timestamp(datetime_string: str):
        try:
            return int(datetime.strptime(datetime_string, "%Y-%m-%d %H:%M").timestamp()) * 1000
        except ValueError:
            raise ValueError(f"Invalid time format '{datetime_string}'. Must be in 'YYYY-MM-DD HH:MM' format.")

    def validate_params(self, category: str, symbol: str, interval: str, start_time: str, end_time: str):
        if category not in self.valid_categories:
            raise ValueError(f"Invalid category '{category}'. Must be one of {self.valid_categories}.")

        if not isinstance(symbol, str) or not symbol:
            raise ValueError(f"Invalid symbol '{symbol}'. Must be a non-empty string.")

        if interval not in valid_intervals:
            raise ValueError(f"Invalid interval '{interval}'. Must be one of {valid_intervals}.")

        start_timestamp: int | None = self.datetime_to_timestamp(start_time) if start_time else None
        end_timestamp: int | None = self.datetime_to_timestamp(end_time) if end_time else None

        if start_timestamp and end_timestamp and start_timestamp >= end_timestamp:
            raise ValueError("start_time must be less than end_time.")

        return start_timestamp, end_timestamp

    def fetch_inverse_klines(self,
                             category: str,
                             symbol: str,
                             interval: str,
                             start_timestamp: str,
                             end_timestamp: str,
                             limit=200):
        url = (f'{self.base_url}/v5/market/kline?'
               f'category={category}&symbol={symbol}&interval={interval}'
               f'&start={start_timestamp}&end={end_timestamp}&limit={limit}')

        data = requests.get(url).json()

        if data.get("retCode") != 0:
            raise Exception(f"API Error: {data.get('retMsg')}")

        klines = data["result"]["list"]
        df = pd.DataFrame(klines, columns=self.columns)
        df["Datetime"] = pd.to_datetime(df["Datetime"].astype(int), unit='ms')
        df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float, "Turnover": float})
        return df.sort_values("Datetime").reset_index(drop=True)

    def fetch_all_klines(self, category: str, symbol: str, interval: str, start_datetime: str, end_datetime: str,
                         limit=200):
        start_timestamp, end_timestamp = self.validate_params(category, symbol, interval, start_datetime, end_datetime)
        all_data = []

        while start_timestamp < end_timestamp:
            df = self.fetch_inverse_klines(category, symbol, interval, start_timestamp, end_timestamp, limit)
            if df.empty:
                break
            all_data.append(df)

            last_timestamp = int(df.iloc[-1]['Datetime'].timestamp()) * 1000
            if last_timestamp >= end_timestamp:
                break

            start_timestamp = last_timestamp + interval_to_milliseconds[interval]
            time.sleep(0.15)

        return pd.concat(all_data).reset_index(drop=True) if all_data else pd.DataFrame()


class BybitDownloader:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.loader = BybitKlinesLoader()
        self.category = "linear"

    def download_data(self, interval: str, start_datetime: str, end_datetime: str):
        return self.loader.fetch_all_klines(
            category=self.category,
            symbol=self.symbol,
            interval=interval,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )


class BybitDataGenerator:
    @staticmethod
    def generate_all_data():
        for interval in INTERVALS:
            BybitDataGenerator.generate_data(interval)

    @staticmethod
    def generate_data(interval: str):
        folder_name = INTERVAL_MAP.get(interval, interval)
        folder_path = os.path.join("../bybit_test_data/csvs", folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for ticker in TICKERS:
            downloader = BybitDownloader(ticker)
            try:
                df = downloader.download_data(interval, START_DATETIME, END_DATETIME)
                if not df.empty:
                    file_path = os.path.join(folder_path, f"{ticker}.csv")
                    df.to_csv(file_path, index=False, sep=',', encoding='utf-8')
                    print(f"Downloaded {ticker} | {interval}")
                else:
                    print(f"No data for {ticker} | {interval}")
            except Exception as e:
                print(f"Error downloading {ticker} | {interval}: {e}")


@time_it
def generate_all_bybit_data():
    BybitDataGenerator.generate_all_data()


if __name__ == '__main__':
    TICKERS = [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "AAVEUSDT",
        "AVAXUSDT"
    ]

    INTERVALS = [
        "1m", "5m", "15m", "30m", "1h", "4h"
    ]

    START_DATETIME = "2024-03-01 00:00"
    END_DATETIME = "2024-05-01 00:00"

    generate_all_bybit_data()
