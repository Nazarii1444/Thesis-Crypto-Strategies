import plotly.graph_objects as go
import pandas as pd
from utils.loader import load_csv


def plot_single_trade(data, start_time, end_time):
    data.index = pd.to_datetime(data.index)
    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    fig = go.Figure()

    # Свічки
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Ціна'
    ))

    # color = 'green' if trade.profit > 0 else 'red'
    color = 'purple'
    start_price = data.loc[start_time, 'Close']
    end_price = data.loc[end_time, 'Close']

    fig.add_trace(go.Scatter(
        x=[start_time], y=[start_price],
        mode='markers',
        marker=dict(color="blue", size=12, symbol='circle'),
        name='Точка входу'
    ))

    fig.add_trace(go.Scatter(
        x=[end_time], y=[end_price],
        mode='markers',
        marker=dict(color="green", size=12, symbol='circle'),
        name='Точка виходу'
    ))

    fig.add_trace(go.Scatter(
        x=[start_time, end_time],
        y=[start_price, end_price],
        mode='lines',
        line=dict(color='purple', dash='dash'),
        name='Лінія трейду'
    ))

    fig.update_layout(
        legend_title="Легенда",
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='white',
        height=500,
        width=800
    )
    fig.update_yaxes(title_text="Ціна")
    fig.show()


if __name__ == '__main__':
    df = load_csv("test_data/custom_csvs/AAVE_USDT_RECENT.csv")

    plot_single_trade(df, "2024-10-12 18:20", "2024-10-13 00:00")
