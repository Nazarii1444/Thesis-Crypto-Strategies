import os
import time
from functools import wraps
from yfdownloader import YFDownloader

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


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'Time taken by {func.__name__}: {elapsed_time:.2f} seconds')
        return result

    return wrapper


class DataGenerator:
    @staticmethod
    def generate_all_data():
        for interval_name, downloader_method in INTERVALS:
            DataGenerator.generate_data(interval_name, downloader_method)

    @staticmethod
    def generate_data(interval_name: str, downloader_method: str):
        folder_path = f'../csvs/{interval_name}'
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
    DataGenerator().generate_all_data()


@time_it
def generate_sixty_days_data():
    """Generates 60 days data with for every timeframe."""
    DataGenerator().generate_sixty_days_data()


if __name__ == '__main__':
    generate_all_data()
