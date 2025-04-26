import plotly.graph_objects as go
from plotly.subplots import make_subplots

from indicators import add_atr
from utils.loader import load_csv

CSV_PATH = "../data_visualization/AAVE_USD_FOR_LINE_CHART.csv"
ATR_PERIOD = 14

if __name__ == '__main__':
    df = load_csv(CSV_PATH)
    df = add_atr(df, ATR_PERIOD)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.03,
        subplot_titles=["Свічковий графік", f"Індикатор ATR ({ATR_PERIOD})"]
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
            y=df[f"ATR_{ATR_PERIOD}"],
            mode="lines",
            name=f"ATR {ATR_PERIOD}",
            line=dict(color="darkgreen", width=2)
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=600,
        width=1200,
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=25, t=60, b=40)
    )

    fig.update_yaxes(title_text="Ціна", row=1, col=1)
    fig.update_yaxes(title_text="ATR", row=2, col=1)

    fig.show()
