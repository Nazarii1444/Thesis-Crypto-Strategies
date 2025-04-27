from typing import List

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from indicators import add_bollinger_bands
from utils.add_trades_marks import add_trades_marks_
from utils.config import LONG, SHORT
from utils.utils import load_csv
from utils.stats import Stats
from utils.trade import Trade


def simulate_macd_atr_strategy(data):
    trades: List[Trade] = []
    position = None
    trade_id = 1
    cash, initial_cash = 1000, 1000
    lot_percentage = 0.12

    bb_period = 20
    bb_std_dev = 2

    data = add_bollinger_bands(data, period=bb_period, std_dev=bb_std_dev)

    for i in range(bb_period, len(data)):
        date = data.index[i]
        current_close = data['Close'].iloc[i]
        upper_band = data['BB_Upper'].iloc[i]
        lower_band = data['BB_Lower'].iloc[i]

        if position is None:
            if current_close > upper_band:
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, LONG, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = LONG
                trade_id += 1

            elif current_close < lower_band:
                amount_in_dollars = cash * lot_percentage / 100
                trades.append(Trade(trade_id, SHORT, amount_in_dollars, current_close, date))
                cash -= amount_in_dollars
                position = SHORT
                trade_id += 1

        elif position == LONG:
            if lower_band < current_close < upper_band:
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)
                position = None

        elif position == SHORT:
            if lower_band < current_close < upper_band:
                trade = trades[-1]
                trade.close(current_close, date, cash)
                cash = trade.portfolio_value_after
                print(trade)
                position = None

    Stats(initial_cash, lot_percentage, trades).export_stats_to_excel()
    plot_trades(data, trades)


def plot_trades(data, trades):
    fig = make_subplots(
        rows=1, cols=1,
        shared_xaxes=True
    )

    fig.add_trace(
        go.Scatter(
            x=data.index.tolist() + data.index[::-1].tolist(),
            y=data['BB_Upper'].tolist() + data['BB_Lower'][::-1].tolist(),
            fill='toself',
            fillcolor='lightblue',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            name='Bollinger Bands Area',
            showlegend=False
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Close Price'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['BB_Upper'],
            mode='lines',
            name='Upper Band',
            line=dict(color='red', dash='dash')
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['BB_Middle'],
            mode='lines',
            name='Middle Band',
            line=dict(color='blue', dash='dot')
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['BB_Lower'],
            mode='lines',
            name='Lower Band',
            line=dict(color='green', dash='dash')
        ),
        row=1, col=1
    )

    fig = add_trades_marks_(trades, fig, row=1, col=1)

    fig.update_layout(
        title="Стратегія базована на Bollinger Bands",
        legend_title="Легенда",
        xaxis_rangeslider_visible=False
    )

    fig.update_xaxes(title_text="Дата", row=1, col=1)
    fig.update_yaxes(title_text="Ціна", row=1, col=1)

    fig.show()


if __name__ == '__main__':
    df = load_csv("../test_data/custom_csvs/AAVE_USDT_RECENT.csv")
    simulate_macd_atr_strategy(df)
