import time
from functools import wraps

import pandas as pd


def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f'Time taken by {func.__name__}: {end_time - start_time:.2f} seconds')
        return result

    return wrapper


def load_csv(filepath):
    with open(filepath, 'r') as file:
        first_line = file.readline()
        columns = first_line.strip().split(',')

    allowed_columns = ['Datetime', 'Date']
    index_col = None
    for col in allowed_columns:
        if col in columns:
            index_col = col

    if index_col is None:
        raise ValueError("CSV does not have 'Datetime' or 'Date'")

    data = pd.read_csv(filepath, index_col=index_col, parse_dates=True)
    return data[data["Volume"] != 0]


def resample_to_15m(filepath, other_filepath):
    data = pd.read_csv(filepath, parse_dates=True, index_col='Datetime')

    resampled_data = data.resample('15T').agg({  # Групування даних за 15-хвилинними інтервалами
        'Open': 'first',  # Перша ціна за 15 хвилин - ціна відкриття
        'High': 'max',  # Найвища ціна за 15 хвилин
        'Low': 'min',  # Найнижча ціна за 15 хвилин
        'Close': 'last',  # Остання ціна за 15 хвилин - ціна закриття
        'Volume': 'sum'  # Сумарний об'єм торгів за 15 хвилин
    })

    resampled_data.to_csv(other_filepath)


def dataframe_cutter(filepath, new_filename, start_date, end_date):
    data = pd.read_csv(filepath)
    data['Datetime'] = pd.to_datetime(data['Datetime'])
    data.set_index('Datetime', inplace=True)

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered_data = data[(data.index >= start_date) & (data.index <= end_date)]
    filtered_data.to_csv(new_filename)


def trim_data_to_one_day(filepath):
    data = load_csv(filepath)

    trimmed_data = data.loc['2024-09-12']
    return trimmed_data.to_csv(filepath)


if __name__ == '__main__':
    dataframe_cutter("../test_data/custom_csvs/AAVE_USDT_1m.csv", "AAVE_USD_FOR_BAR_CHART.csv", '2023-10-29 12:00',
                     '2023-10-30 13:00')
