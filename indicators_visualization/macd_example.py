import plotly.graph_objects as go
from plotly.subplots import make_subplots

from indicators import add_macd
from utils.loader import load_csv

CSV_PATH = "../data_visualization/AAVE_USD_FOR_LINE_CHART.csv"
FAST = 12
SLOW = 26
SIGNAL = 9

if __name__ == '__main__':
    df = load_csv(CSV_PATH)
    df = add_macd(df, FAST, SLOW, SIGNAL)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.03,
        subplot_titles=["Свічковий графік", "Індикатор MACD"]
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Свічки"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MACD"],
            mode="lines",
            name="MACD",
            line=dict(color="blue", width=1.5)
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MACD_Signal"],
            mode="lines",
            name="Сигнальна лінія",
            line=dict(color="orange", width=1.5)
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["MACD_Hist"].where(df["MACD_Hist"] >= 0),
            name="MACD Гістограма (Додатня)",
            marker_color="green",
            showlegend=True,
            width = 60_000
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["MACD_Hist"].where(df["MACD_Hist"] < 0),
            name="MACD Гістограма (Від’ємна)",
            marker_color="red",
            showlegend=True,
            width=60_000
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=500,
        width=1200,
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=25, t=60, b=40)
    )

    fig.update_yaxes(title_text="Ціна", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)

    fig.show()
