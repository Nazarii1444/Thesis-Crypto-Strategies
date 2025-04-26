import plotly.graph_objects as go
from plotly.subplots import make_subplots

from indicators import add_stochastic_oscillator
from utils.loader import load_csv

CSV_PATH = "../data_visualization/AAVE_USD_FOR_LINE_CHART.csv"
K_PERIOD = 14
D_PERIOD = 3

if __name__ == '__main__':
    df = load_csv(CSV_PATH)
    df = add_stochastic_oscillator(df, K_PERIOD, D_PERIOD)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.75, 0.25],
        vertical_spacing=0.03,
        subplot_titles=["Свічковий графік", "Стохастичний осцилятор (%K і %D)"]
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

    # %K
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["%K"],
            mode="lines",
            name="%K",
            line=dict(color="blue", width=2)
        ),
        row=2, col=1
    )

    # %D
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["%D"],
            mode="lines",
            name="%D",
            line=dict(color="orange", width=2)
        ),
        row=2, col=1
    )

    fig.add_hline(y=20, line=dict(color="gray", dash="dot"), row=2, col=1)
    fig.add_hline(y=80, line=dict(color="gray", dash="dot"), row=2, col=1)

    fig.update_layout(
        height=600,
        width=900,
        margin=dict(l=50, r=25, t=60, b=40),
        xaxis_rangeslider_visible=False
    )

    fig.update_yaxes(title_text="Ціна", row=1, col=1)
    fig.update_yaxes(title_text="Stochastic", row=2, col=1, range=[0, 100])

    fig.show()
