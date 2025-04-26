import plotly.graph_objects as go
from plotly.subplots import make_subplots

from indicators import add_rsi
from utils.loader import load_csv

CSV_PATH = "../data_visualization/AAVE_USD_FOR_LINE_CHART.csv"
FAST_PERIOD = 14
SLOW_PERIOD = 21

if __name__ == '__main__':
    df = load_csv(CSV_PATH)
    df = add_rsi(df, FAST_PERIOD)
    df = add_rsi(df, SLOW_PERIOD)

    fast_col = f"RSI_{FAST_PERIOD}"
    slow_col = f"RSI_{SLOW_PERIOD}"

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.03,
        subplot_titles=("Свічковий графік", f"RSI ({FAST_PERIOD}, {SLOW_PERIOD})")
    )

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            showlegend=False,
            name="Свічки"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[fast_col],
            mode="lines",
            name=f"RSI {FAST_PERIOD}",
            line=dict(width=2.0, color="black")
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[slow_col],
            mode="lines",
            name=f"RSI {SLOW_PERIOD}",
            line=dict(width=2.0, color="green")
        ),
        row=2, col=1
    )

    fig.add_hline(y=30, line=dict(color="black", width=1, dash="dot"),
                  row=2, col=1)
    fig.add_hline(y=70, line=dict(color="black", width=1, dash="dot"),
                  row=2, col=1)

    fig.update_layout(
        height=700,
        width=1000,
        template="seaborn",
        margin=dict(l=50, r=25, t=60, b=40),
        xaxis_rangeslider_visible=False
    )

    fig.update_yaxes(title_text="Ціна", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])

    fig.show()
