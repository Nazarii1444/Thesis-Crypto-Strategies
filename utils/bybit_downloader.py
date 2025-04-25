import requests
import pandas as pd
import time
from datetime import datetime


class BybitKlinesLoader:
    def __init__(self):
        self.base_url = "https://api.bybit.com"
        self.valid_intervals = {
            '1m': 1, '3m': 3, '5m': 5, '15m': 15, '30': 30, '1h': 60,
            '2h': 120, '4h': 240, '6h': 360, '8h': 480, '12h': 720, '1d': 'D', '1w': 'W'
        }
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

        if not isinstance(symbol, str) or not symbol.isalnum():
            raise ValueError(f"Invalid symbol '{symbol}'. Must be a non-empty alphanumeric string.")

        if interval not in self.valid_intervals:
            raise ValueError(f"Invalid interval '{interval}'. Must be one of {self.valid_intervals}.")

        start_timestamp: int | None = self.datetime_to_timestamp(start_time) if start_time else None
        end_timestamp: int | None = self.datetime_to_timestamp(end_time) if end_time else None

        if start_timestamp and end_timestamp and start_timestamp >= end_timestamp:
            raise ValueError("start_time must be less than end_time.")

        return start_timestamp, end_timestamp

    def fetch_inverse_klines(self, category: str, symbol: str, interval: str, start_timestamp: str, end_timestamp: str,
                             limit=200):
        interval = self.valid_intervals[interval]
        url = (f'https://api.bybit.com/v5/market/kline?'
               f'category={category}&symbol={symbol}&interval={interval}&start={start_timestamp}&end={end_timestamp}')

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

            start_timestamp = last_timestamp + 1
            time.sleep(0.15)

        return pd.concat(all_data).reset_index(drop=True) if all_data else pd.DataFrame()


if __name__ == '__main__':
    loader = BybitKlinesLoader()
    df = loader.fetch_all_klines(
        category='inverse',
        symbol='BTCUSDT',
        interval='1m',
        start_datetime='2025-03-04 00:00',
        end_datetime='2025-03-04 06:00',
        limit=100
    )
    print(df)
