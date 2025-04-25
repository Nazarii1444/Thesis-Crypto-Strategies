from indicators import add_rsi
from utils.loader import load_csv

if __name__ == '__main__':
    filepath = "./test_data/csvs/fifteen_m/AAVE_USD.csv"
    df = load_csv(filepath)
    df.drop(columns=["Adj Close"], inplace=True)
    df = add_rsi(df, 14)
    df.loc[:, df.columns != "Datetime"] = df.loc[:, df.columns != "Datetime"].round(3)
    df = df.to_excel("rsi_example.xlsx")
