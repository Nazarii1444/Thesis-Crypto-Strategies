import plotly.graph_objects as go

from indicators import add_ema
from utils.loader import load_csv

CSV_PATH = "../data_visualization/AAVE_USD_FOR_LINE_CHART.csv"
FAST_PERIOD = 14
SLOW_PERIOD = 40

if __name__ == '__main__':
    df = load_csv(CSV_PATH)

    df = add_ema(df, FAST_PERIOD)
    df = add_ema(df, SLOW_PERIOD)

    fast_col = f"EMA_{FAST_PERIOD}"
    slow_col = f"EMA_{SLOW_PERIOD}"

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                showlegend=False
            )
        ]
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[fast_col],
            mode="lines",
            name=f"EMA {FAST_PERIOD}",
            line=dict(width=2.0, color="black")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[slow_col],
            mode="lines",
            name=f"EMA {SLOW_PERIOD}",
            line=dict(width=2.0, color="green")
        )
    )

    fig.update_layout(
        title="Свічковий графік",
        xaxis_title="Час",
        yaxis_title="Ціна",
        xaxis_rangeslider_visible=False,
        template="seaborn",
        height=600,
        width=1000,
        margin=dict(l=50, r=25, t=60, b=40)
    )

    fig.show()
