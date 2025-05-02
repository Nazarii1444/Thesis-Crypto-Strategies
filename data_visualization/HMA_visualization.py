import pandas as pd
import plotly.graph_objects as go

from utils.indicators import add_hma
from utils.utils import load_csv


def add_second_derivative(df: pd.DataFrame, column: str, new_col: str = None) -> pd.DataFrame:
    if column not in df.columns:
        raise ValueError(f"Колонка '{column}' не знайдена в DataFrame.")

    if new_col is None:
        new_col = f'{column}_2nd_deriv'

    # друга похідна
    df[new_col] = df[column].diff().diff()
    return df


def visualize_hma(filepath: str, period: int):
    df = load_csv(filepath)
    df.index = pd.to_datetime(df.index)

    df = add_hma(df, period)
    hma_column = f"HMA_{period}"
    df = add_second_derivative(df, hma_column)

    if hma_column not in df.columns:
        raise ValueError(f"Колонка {hma_column} відсутня після виклику add_hma.")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Ціна',
        line=dict(color='red')
    ))

    # HMA
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[hma_column],
        mode='lines',
        name=f'HMA {period}',
        line=dict(color='black')
    ))

    fig.update_layout(
        title=f'Hull Moving Average ({period})',
        xaxis_title='Час',
        yaxis_title='Ціна',
        xaxis_rangeslider_visible=False,
        height=600
    )

    fig.show()


if __name__ == '__main__':
    filepath = '../custom_test_data/custom_csvs/AAVE_USDT_RECENT.csv'
    visualize_hma(filepath, period=25)
