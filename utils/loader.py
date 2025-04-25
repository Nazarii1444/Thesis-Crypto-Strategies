import pandas as pd


def load_csv(filepath):
    with open(filepath, 'r') as file:
        first_line = file.readline()
        columns = first_line.strip().split(',')

    if 'Datetime' in columns:
        index_col = 'Datetime'
    elif 'Date' in columns:
        index_col = 'Date'
    else:
        raise ValueError("CSV файл не містить стовпців 'Datetime' або 'Date'")

    data = pd.read_csv(filepath, index_col=index_col, parse_dates=True)
    return data[data["Volume"] != 0]
