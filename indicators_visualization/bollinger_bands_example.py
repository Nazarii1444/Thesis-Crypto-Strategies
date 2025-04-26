import plotly.graph_objects as go

from indicators import add_bollinger_bands
from utils.loader import load_csv

CSV_PATH = "../data_visualization/AAVE_USD_FOR_LINE_CHART.csv"
BB_PERIOD = 20
STD_MULT = 2

if __name__ == '__main__':
    df = load_csv(CSV_PATH)
    df = add_bollinger_bands(df, BB_PERIOD, STD_MULT)

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Свічки"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Middle"],
            mode="lines",
            name=f"MA {BB_PERIOD}",
            line=dict(color="red", width=1.5)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Upper"],
            mode="lines",
            name="BB Верхня",
            line=dict(color="blue", width=1),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Lower"],
            mode="lines",
            name="BB Нижня",
            line=dict(color="blue", width=1),
            fill='tonexty',
            fillcolor='rgba(173, 216, 230, 0.2)'
        )
    )

    fig.update_layout(
        title="Bollinger Bands",
        xaxis_title="Час",
        yaxis_title="Ціна, USD",
        height=600,
        width=1000,
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=25, t=60, b=40)
    )

    fig.show()
