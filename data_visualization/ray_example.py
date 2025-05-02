import pandas as pd
import plotly.graph_objects as go

from utils.utils import load_csv


def ray_intersections(filepath: str, datetime_str: str) -> int:
    df = load_csv(filepath)
    df.index = pd.to_datetime(df.index)

    target_time = pd.to_datetime(datetime_str)
    if target_time not in df.index:
        raise ValueError(f"No such data: {datetime_str}.")

    current_close = df.loc[target_time, 'Close']

    df_future = df.loc[target_time:].copy()
    df_future['prev'] = df_future['Close'].shift(1)

    df_future = df_future.dropna()
    df_future['cross'] = ((df_future['Close'] >= current_close) & (df_future['prev'] < current_close)) | \
                         ((df_future['Close'] <= current_close) & (df_future['prev'] > current_close))
    crossings = df_future['cross'].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Ціна', line=dict(color='blue')))
    fig.add_trace(go.Scatter(
        x=[target_time, df.index[-1]],
        y=[current_close, current_close],
        mode='lines',
        name=f'Промінь від {datetime_str}',
        line=dict(color='red', dash='dash')
    ))

    fig.update_layout(
        title=f'Кількість перетинів ціни з променем: {crossings}',
        xaxis_title="Час",
        yaxis_title="Ціна",
        xaxis_rangeslider_visible=False,
        height=750
    )
    fig.show()

    return int(crossings)


if __name__ == '__main__':
    filepath = '../custom_test_data/custom_csvs/AAVE_USDT_RECENT.csv'
    date = "2024-10-02"
    ray_intersections(filepath, date)
